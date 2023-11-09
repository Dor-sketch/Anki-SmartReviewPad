"""
This module is responsible for handling the card review process.
"""
import re
import logging
import os
import subprocess
from aqt import mw
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from .my_card import AnkiCardWrapper
from .strikecounter import GlobalStrikeCounter
from .logger import initialize_logging
from .hebrewhandler import HebrewHandler


KEY_EVENTS_SCRIPT = """
            document.querySelector('#scratchpad').addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    document.querySelector('#back-container').style.display = 'block';
                    this.blur();
                    pybridge.send('enter_pressed');
                    pycmd('enter_pressed');
                }
            });
        """

SCRACTHPAD_HTML = """<div id='scratchpad-container' style='display: flex; justify-content: center; align-items: center; height: 100%;'>
                <textarea id='scratchpad' dir='rtl' style='font-size: 24px; background-color: rgb(245, 245, 245);'></textarea>
              </div>"""

PANDOC_PATH = '/usr/local/bin/pandoc'


INLINE_MATH_PATTERN = re.compile(r"""
    \\\(   # Matches the opening delimiter \(
    (.*?)  # Captures everything lazily until it encounters the closing delimiter
    \\\)   # Matches the closing delimiter \)
""", re.VERBOSE)

CLOZE_PATTERN = re.compile(r"""
    {{c      # Matches the opening cloze notation {{c
    (\d+)    # Captures one or more digits, representing the cloze number
    ::       # Matches the delimiter between the cloze number and its content
    (.+?)    # Lazily captures the content of the cloze until the closing }}
    }}       # Matches the closing cloze notation }}
""", re.VERBOSE)



def my_get_scratchpad(card) -> None:
    """
    This function is called when the card is shown.
    """
    mw.reviewer.card_reviewer.get_scratchpad(card)


gui_hooks.reviewer_did_show_answer.append(my_get_scratchpad)


class CardReviewer:
    """
    This class is responsible for handling the card review process.
    """

    def __init__(self, reviewer: Reviewer):
        self.scratchpad_content = None
        self.reviewer = reviewer
        self.card_wrapper = None
        self._initialize_logging()
        self._setup_bridge_command()
        self._initialize_link_handler()
        self.cloze_answer = None

    def _initialize_logging(self):
        initialize_logging()
        self.card_reviewer_logger = logging.getLogger("anki_addon")
        self.card_reviewer_logger.setLevel(logging.DEBUG)
        self.card_reviewer_logger.propagate = False

    def _setup_bridge_command(self):
        original_onBridgeCmd = self.reviewer.web.onBridgeCmd
        self.reviewer.web.onBridgeCmd = lambda msg: [
            self._handle_bridge_message(msg), original_onBridgeCmd(msg)]

    def _initialize_link_handler(self):
        original_link_handler = self.reviewer._linkHandler
        self.reviewer._linkHandler = lambda url: [
            self._handle_bridge_message(url), original_link_handler(url)]

    def _handle_bridge_message(self, message):
        if message == "enter_pressed":
            self._log_and_speak("Received enter_pressed")

    def _log_and_speak(self, message):
        self.card_reviewer_logger.debug(message)




    def _update_card_review(self, card=None):
        card = mw.reviewer.card
        fields = card.note().fields
        front_field = self._find_first_non_empty_field(fields)
        self._inject_card_html(
            self._build_front_html(front_field),
            self._build_scratchpad_html(),
            self._build_back_html(fields, front_field)
        )
        self.card_wrapper = AnkiCardWrapper(card)
        logging.info("Card wrapper: %s", self.card_wrapper)
        self._add_key_events()
        self.focus_scratchpad()

    def _find_first_non_empty_field(self, fields):
        return next((field for field in fields if not field.startswith("[sound:") and field.strip()), None)

    def _find_clozes(self, front_field):
        """
        Find all cloze deletions in the given field text and return them.
        """
        return CLOZE_PATTERN.findall(front_field)

    def _build_front_html(self, front_field):
        """
        Build the HTML for the front of the card, showing only the current cloze.
        """
        self.card_reviewer_logger.debug("Front field before: %s", front_field)
        cloze_number = self.reviewer.card.ord + 1  # Get the current cloze number
        clozes = self._find_clozes(front_field)

        for cn, content in clozes:
            if int(cn) == cloze_number:
                # Replace only the current cloze with a placeholder for the scratchpad
                front_field = re.sub(rf"{{{{c{cn}::(.+?)}}}}", r"{}", front_field)
                self.cloze_answer = content
                self.card_reviewer_logger.debug("content: %s", content)
            else:
                # Replace other clozes with their contents directly, removing cloze notation
                front_field = re.sub(rf"{{{{c{cn}::(.+?)}}}}", r"\1", front_field)


            self.card_reviewer_logger.debug("Front field after cloze extract: %s", front_field)

        if "$$" in front_field or "\\(" in front_field:
            front_field = self._render_math(front_field)
            self.card_reviewer_logger.debug(
                "Front field after math: %s", front_field)

        # TODO: Move scripts to separate file
        return f"<div id='front-container' style='display: flex; flex-direction: column; align-items: center; font-size: 24px;'><div class='field'>{front_field}</div></div>"

    def _build_back_html(self, fields, front_field):
        self.card_reviewer_logger.debug("Fields: %s", fields)
        if self.cloze_answer is not None:
            return f"<div id='back-container' style='display: none; text-align: center; font-size: 24px;'><div class='field'>{self.cloze_answer}</div></div>"
        return "<div id='back-container' style='display: none; text-align: center; font-size: 24px;'>" + \
               "".join([f"<div class='field'>{field}</div>" for field in fields if "sound" not in field and field.strip() and field != front_field]) + \
               "</div>"

    def _build_scratchpad_html(self):
        self.card_reviewer_logger.debug("Building scratchpad HTML")
        cols_value = "20"  # Default size
        if self.cloze_answer is not None:
            cols_value = str(len(self.cloze_answer))
            return f"""<div id='scratchpad-container' style='display: inline-block; justify-content: center; align-items: center;'>
                <textarea id='scratchpad' dir='rtl' cols='{cols_value}' style='font-size: 24px; background-color: rgb(245, 245, 245);'></textarea>
                </div>"""
        else:
            return SCRACTHPAD_HTML

    def _find_inline_math(self, text):
        return INLINE_MATH_PATTERN.findall(text)

    def _render_math(self, text):
        # Find all inline math expressions
        inline_math = self._find_inline_math(text)
        inline_math = [f"\\({expr}\\)" for expr in inline_math]

        # Check if pandoc exists
        if os.path.exists(PANDOC_PATH):
            # Render each inline math expression
            rendered_inline_math = []
            for expr in inline_math:
                # TODO: Handle errors
                # try:
                #     result = subprocess.run(
                #         [PANDOC_PATH, '-f', 'latex', '-t', 'html'],
                #         input=expr,
                #         text=True,
                #         capture_output=True,
                #         encoding='utf-8',  # Added encoding to handle non-ASCII characters
                #         check=True  # Automatically raise an error if the command fails
                #     )
                #     rendered_math = result.stdout.strip().replace("<p>", "").replace("</p>", "")
                #     rendered_inline_math.append(rendered_math)
                # except subprocess.CalledProcessError as e:
                #     self.card_reviewer_logger.debug(
                #         "Pandoc failed with error code %d: %s", e.returncode, e.stderr)
                #     return text  # Return original text if error occurs
                # except Exception as e:
                #     self.card_reviewer_logger.debug(
                #         "Error occurred while running pandoc: %s", e)
                #     return text  # Return original text if error occurs
                try:
                    result = subprocess.run(
                        [PANDOC_PATH, '-f', 'latex', '-t', 'html'],
                        input=expr,
                        text=True,
                        capture_output=True,
                        encoding='utf-8'  # handle non-ASCII characters
                    )
                    if result.returncode == 0:
                        rendered_math = result.stdout.strip().replace("<p>", "").replace("</p>", "")
                        rendered_inline_math.append(rendered_math)
                    else:
                        self.card_reviewer_logger.debug(
                            "Pandoc failed with error code %d: %s", result.returncode, result.stderr)
                        return text  # Return original text if error occurs
                except Exception as e:
                    self.card_reviewer_logger.debug(
                        "Error occurred while running pandoc: %s", e)
                    return text  # Return original text if error occurs
        else:
            self.card_reviewer_logger.debug("Pandoc path does not exist.")
            return text  # Return original text if pandoc path doesn't exist

        # Replace original inline math expressions with their rendered counterparts
        for original, rendered in zip(inline_math, rendered_inline_math):
            text = text.replace(original, rendered)

        return text

    def _inject_card_html(self, front_html, scratchpad_html, back_html):
        self.card_reviewer_logger.debug(
            "Injecting card HTML (font is): %s", front_html)

        if self.cloze_answer is not None:
            # place scratchpad in the cloze position
            scratchpad_html_adjusted = scratchpad_html.replace(
                "<textarea",
                "<textarea style='vertical-align: middle;'"
            )
            front_html = re.sub(r"{}", scratchpad_html_adjusted, front_html)

            mw.reviewer.web.eval(
                f"document.querySelector('.card').innerHTML = `{front_html}<br><br>{back_html}`;"
            )

        else:

            mw.reviewer.web.eval(
                f"document.querySelector('.card').innerHTML = `{front_html}<br><br>{scratchpad_html}<br>{back_html}`;")

    def _add_key_events(self):
        mw.reviewer.web.eval(KEY_EVENTS_SCRIPT)

    def focus_scratchpad(self):
        """
        Focuses the scratchpad element.
        """
        mw.reviewer.web.eval("document.querySelector('#scratchpad').focus();")

    def get_scratchpad(self, card=None):
        """
        Gets the scratchpad content and calls the callback function.
        An entry point for the flow.
        """
        mw.reviewer.web.evalWithCallback(
            "document.querySelector('#scratchpad').value", self.my_callback)

    def my_callback(self, result):
        """
        This function is called when the scratchpad content is retrieved.
        """
        if result is not None:
            self.card_reviewer_logger.debug("Callback result: %s", result)
            self.scratchpad_content = result  # Set attribute value
            self.check_answer(result)  # Continue the flow

    def check_answer(self, scratchpad_content):
        """
        Checks the answer and updates the strike counter accordingly.
        """

        scratchpad_words = set(re.split(r'\W+', scratchpad_content))
        
        if self.cloze_answer is not None:
            all_content_words = set(
                [word for word in re.split(r'\W+', self.cloze_answer) if word])
            self.cloze_answer = None

        else:
            scratchpad_words = HebrewHandler.extract_content_words(
                [scratchpad_content])
            all_content_words = HebrewHandler.extract_content_words(
                self.card_wrapper.fields)

        strike_counter_instance = GlobalStrikeCounter()  # Get the Singleton instance

        # one word is enough
        intersection_result = scratchpad_words & all_content_words

        if scratchpad_words is not None:
            if intersection_result:
                self.card_reviewer_logger.debug("Correct answer")
                strike_counter_instance.increment()
            else:
                self.card_reviewer_logger.debug("Wrong answer: expected %s, got %s",
                                                all_content_words, scratchpad_words)
                strike_counter_instance.reset()


# TODO:: Implement MathHandler class to accordint to SRP and OCP

# TODO:: Implement ClozeHandler class to accordint to SRP and OCP
