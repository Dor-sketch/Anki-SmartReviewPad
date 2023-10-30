from aqt import mw
from anki.hooks import addHook
from aqt.reviewer import Reviewer
from anki.hooks import wrap

def my_function():
    # Get the current card and its fields
    card = mw.reviewer.card
    fields = card.note().fields

    # Find the first non-empty field
    front_field = next((field for field in fields if not field.startswith("[sound:") and field.strip()), None)

    # Build the HTML for the front and back of the card
    front_html = f"<div id='front-container' style='display: flex; flex-direction: column; align-items: center; font-size: 24px;'><div class='field'>{front_field}</div></div>"

    # Build the HTML for the back of the card
    back_html = "<div id='back-container' style='display: none; text-align: center; font-size: 24px;'>"
    for field in fields:
        if "sound" not in field and field.strip() and field not in front_field:
            back_html += f"<div class='field'>{field}</div>"
    back_html += "</div>"


    # Build the HTML for the scratchpad
    scratchpad_html = "\n\n\n<div id='scratchpad-container'><textarea id='scratchpad' dir='rtl' style='font-size: 24px; background-color: rgb(245, 245, 245);'></textarea></div>"

    # Update the card HTML to show the front, scratchpad, and back with the back fields initially hidden
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

    # Add a keydown event listener to the scratchpad
    mw.reviewer.web.eval("""
        var scratchpad = document.querySelector('#scratchpad');
        scratchpad.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                // Show the back of the card
                document.querySelector('#back-container').style.display = 'block';
                // Move the cursor out of the scratchpad
                scratchpad.blur();
                event.preventDefault();
            }
        });
    """)


addHook("showQuestion", my_function)


def focus_scratchpad():
    mw.reviewer.web.eval("""
        var scratchpad = document.querySelector('#scratchpad');
        scratchpad.focus();
    """)

addHook("showQuestion", focus_scratchpad)
