"""
This file is used to initialize the add-on.
It is used to replace Anki's main window reviewer with your custom reviewer.
"""
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from aqt import mw
from .cardreviewer import CardReviewer  # Ensure this import is correct

class MyReviewer(Reviewer):
    """
    Wrapper class for Anki cards. It is used to access information about the card and modify it.
    """
    def __init__(self, mw):
        super().__init__(mw)
        self.card_reviewer = CardReviewer(self)

    def onBridgeCmd(self, cmd):
        super().onBridgeCmd(cmd)
        self.card_reviewer._handle_bridge_message(cmd)

# Replace Anki's main window reviewer with your custom reviewer
mw.reviewer = MyReviewer(mw)

# Define your hook functions
def my_update_card_review(card):
    """
    This function is called when the reviewer is shown.
    """
    mw.reviewer.card_reviewer._update_card_review(card)

def my_get_scratchpad(card):
    mw.reviewer.card_reviewer.get_scratchpad(card)

# Use gui_hooks to append your functions
gui_hooks.reviewer_did_show_question.append(my_update_card_review)
