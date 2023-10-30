from aqt import mw
from anki.hooks import addHook
from aqt.reviewer import Reviewer
from anki.hooks import wrap


class CardReviewer:
    """
    CardReviewer is a class that manages the card layout during the review process.
    """

    def __init__(self, reviewer):
        self.reviewer = reviewer

    def update_card_review(self):
        """
        Updates the card layout during the review process.
        """
        card = mw.reviewer.card
        fields = card.note().fields
        front_field = self.find_first_non_empty_field(fields)

        front_html = self.build_front_html(front_field)
        back_html = self.build_back_html(fields, front_field)
        scratchpad_html = self.build_scratchpad_html()

        self.inject_card_html(front_html, scratchpad_html, back_html)
        self.add_keydown_event_listener()

    def find_first_non_empty_field(self, fields):
        """
        Finds the first non-empty field in a list of fields.
        """
        return next((field for field in fields if not field.startswith("[sound:") and field.strip()), None)

    def build_front_html(self, front_field):
        """
        Builds the HTML for the front of the card.
        """
        return f"<div id='front-container' style='display: flex; flex-direction: column; align-items: center; font-size: 24px;'><div class='field'>{front_field}</div></div>"

    def build_back_html(self, fields, front_field):
        """
        Builds the HTML for the back of the card.
        """
        back_html = "<div id='back-container' style='display: none; text-align: center; font-size: 24px;'>"
        for field in fields:
            if "sound" not in field and field.strip() and field not in front_field:
                back_html += f"<div class='field'>{field}</div>"
        back_html += "</div>"
        return back_html

    def build_scratchpad_html(self):
        """
        Builds the HTML for the scratchpad.
        """
        return "<div id='scratchpad-container'><textarea id='scratchpad' dir='rtl' style='font-size: 24px; background-color: rgb(245, 245, 245);'></textarea></div>"

    def inject_card_html(self, front_html, scratchpad_html, back_html):
        """
        Injects the HTML into the card layout.
        """
        mw.reviewer.web.eval(f"""
            var card = document.querySelector('.card');
            card.innerHTML = `{front_html}<br><br>\n\n\n{scratchpad_html}\n<br>{back_html}`;
            card.style.display = 'flex';
            card.style.flexDirection = 'column';
            card.style.alignItems = 'center';
            card.style.justifyContent = 'space-between';
            card.style.height = '100%';
            card.style.overflow = 'hidden';
        """)

    def add_keydown_event_listener(self):
        """
        Adds a keydown event listener to the scratchpad.
        """
        mw.reviewer.web.eval("""
            var scratchpad = document.querySelector('#scratchpad');
            scratchpad.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    document.querySelector('#back-container').style.display = 'block';
                    scratchpad.blur();
                    event.preventDefault();
                }
            });
        """)

    def focus_scratchpad(self):
        """
        Focuses the cursor on the scratchpad.
        """
        mw.reviewer.web.eval("""
            var scratchpad = document.querySelector('#scratchpad');
            scratchpad.focus();
        """)

# Hook into Anki
card_reviewer = CardReviewer(mw.reviewer)
addHook("showQuestion", card_reviewer.update_card_review)
