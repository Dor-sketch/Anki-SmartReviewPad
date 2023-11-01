import re
import logging
from aqt import mw
from aqt.reviewer import Reviewer
from aqt import gui_hooks
from .my_card import AnkiCardWrapper
from .strikecounter import GlobalStrikeCounter
from .logger import initialize_logging



HEBREW_CHAR_RANGE = r'[\u05D0-\u05EA]'  # Range for Hebrew letters excluding punctuation
HIRIK = "\u05B4"  # Hirik unicode
HOLAM = "\u05B9"  # Holam unicode
NIKKUD_RANGE = r'[\u0591-\u05C7]'  # Range for other Niqqud characters


def replace_hirik_with_yud(text):
    """
    Replaces the Hirik (dot under word) with its equivalent "י", but only if "י" doesn't immediately follow it.
    """
    return re.sub(f"{HIRIK}(?!י)", "י", text)

def replace_holam_with_vav(text):
    """
    Replaces the Holam (dot above word) with its equivalent "ו", but only if "ו" doesn't immediately follow or precede it.
    """
    return re.sub(f"(?<!ו){HOLAM}(?!ו)", "ו", text)


def remove_nikkud(text):
    """
    Removes all Niqqud from the given text and replaces Hirik and Holam with their equivalent 'י' and 'ו'
    :param text: Text to modify
    :return: Modified text
    """
    # Replace Hirik with its equivalent "י"
    text = replace_hirik_with_yud(text)

    # Replace Holam with its equivalent "ו"
    text = replace_holam_with_vav(text)

    # Remove other Niqqud
    nikkud = re.compile(NIKKUD_RANGE)
    return nikkud.sub('', text)


def my_get_scratchpad(card) -> None:
    mw.reviewer.card_reviewer.get_scratchpad(card)


gui_hooks.reviewer_did_show_answer.append(my_get_scratchpad)





class CardReviewer:

    def __init__(self, reviewer: Reviewer):
        self.scratchpad_content = None
        initialize_logging()
        self.card_reviewer_logger = logging.getLogger("anki_addon")
        self.card_reviewer_logger.setLevel(logging.DEBUG)
        self.card_reviewer_logger.propagate = False
        self.card_reviewer_logger.debug("Initializing CardReviewer")
        self.reviewer = reviewer
        # Initialize to None here and set when a card is actually being reviewed
        self.card_wrapper = None
        self.initialize_link_handler()
        self.setup_bridge_command()

    def setup_bridge_command(self):
        original_onBridgeCmd = self.reviewer.web.onBridgeCmd

        def extended_onBridgeCmd(message):
            original_onBridgeCmd(message)
            self.handle_bridge_message(message)

        self.reviewer.web.onBridgeCmd = extended_onBridgeCmd

    def handle_bridge_message(self, message):
        self.card_reviewer_logger.debug(f"Received bridge message: {message}")
        if message == "enter_pressed":
            pass  # only for debugging

    def initialize_link_handler(self):
        original_link_handler = self.reviewer._linkHandler

        def extended_link_handler(url):
            original_link_handler(url)
            self.handle_bridge_message(url)

        self.reviewer._linkHandler = extended_link_handler

    def log_and_speak(self, message):
        self.card_reviewer_logger.debug(message)

    def update_card_review(self, card=None):
        self.log_and_speak("Updating card review")
        self.set_card_html()
        self.add_key_events()

    def set_card_html(self):
        card = mw.reviewer.card
        fields = card.note().fields
        front_field = self.find_first_non_empty_field(fields)
        self.inject_card_html(
            self.build_front_html(front_field),
            self.build_scratchpad_html(),
            self.build_back_html(fields, front_field)
        )
        self.card_wrapper = AnkiCardWrapper(card)
        logging.critical(f"Card: {card}")
        logging.info(f"Card wrapper: {self.card_wrapper}")
        self.add_key_events()
        self.focus_scratchpad()

    def find_first_non_empty_field(self, fields):
        return next((field for field in fields if not field.startswith("[sound:") and field.strip()), None)

    def build_front_html(self, front_field):
        self.card_reviewer_logger.debug(f"Front field: {front_field}")
        return f"<div id='front-container' style='display: flex; flex-direction: column; align-items: center; font-size: 24px;'><div class='field'>{front_field}</div></div>"

    def build_back_html(self, fields, front_field):
        self.card_reviewer_logger.debug(f"Fields: {fields}")
        return "<div id='back-container' style='display: none; text-align: center; font-size: 24px;'>" + \
               "".join([f"<div class='field'>{field}</div>" for field in fields if "sound" not in field and field.strip() and field != front_field]) + \
               "</div>"

    def build_scratchpad_html(self):
        self.card_reviewer_logger.debug("Building scratchpad HTML")
        return """<div id='scratchpad-container' style='display: flex; justify-content: center; align-items: center; height: 100%;'>
                <textarea id='scratchpad' dir='rtl' style='font-size: 24px; background-color: rgb(245, 245, 245);'></textarea>
              </div>"""

    def inject_card_html(self, front_html, scratchpad_html, back_html):
        self.card_reviewer_logger.debug("Injecting card HTML: {}".format(str(front_html)))
        mw.reviewer.web.eval(
            f"document.querySelector('.card').innerHTML = `{front_html}<br><br>{scratchpad_html}<br>{back_html}`;")

    def add_key_events(self):
        mw.reviewer.web.eval("""
            document.querySelector('#scratchpad').addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    document.querySelector('#back-container').style.display = 'block';
                    this.blur();
                    pybridge.send('enter_pressed');
                    pycmd('enter_pressed');
                }
            });
        """)

    def focus_scratchpad(self):
        mw.reviewer.web.eval("document.querySelector('#scratchpad').focus();")

    def get_scratchpad(self, card=None):
        mw.reviewer.web.evalWithCallback(
            "document.querySelector('#scratchpad').value", self.my_callback)

    def my_callback(self, result):
        if result is not None:
            self.card_reviewer_logger.debug(
                f"Scratchpad callback result: {result}")
            self.scratchpad_content = result  # Set attribute value
            self.check_answer(result)  # Continue the flow

    def check_answer(self, scratchpad_content):

        scratchpad_words = set(re.findall(
            f'{HEBREW_CHAR_RANGE}+', scratchpad_content))

        # Remove Nikkud from each field individually
        all_content = [remove_nikkud(field)
                       for field in self.card_wrapper.fields]
        all_content_words = set(word for field in all_content for word in re.findall(
            f'{HEBREW_CHAR_RANGE}+', field))
        self.card_reviewer_logger.debug(
            f"All content words: {all_content_words}")

        strike_counter_instance = GlobalStrikeCounter()  # Get the Singleton instance

        if scratchpad_words & all_content_words and scratchpad_words is not None:
            self.card_reviewer_logger.debug("Correct answer")
            strike_counter_instance.increment()
        else:
            self.card_reviewer_logger.debug("Incorrect answer")
            strike_counter_instance.reset()
