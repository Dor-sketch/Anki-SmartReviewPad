"""
This file contains a wrapper class for Anki cards. It is used to access
information about the card and modify it.
"""
import logging
import os
from aqt import mw


def initialize_logging():
    """
    Initializes logging for the addon.
    """
    log_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'anki_addon.log')
    logging.basicConfig(filename=log_path, filemode='a', level=logging.DEBUG)


class AnkiCardWrapper:
    """
    Wrapper class for Anki cards. It is used to access information about the card and modify it.
    """

    def __init__(self, card):
        self.card = card

    @property
    def note(self):
        return self.card.note()

    @property
    def id(self):
        return self.card.id

    @property
    def deck_id(self):
        return self.card.did

    @property
    def fields(self):
        return self.note.fields

    def field(self, field_name):
        return self.note.fields[self.note._model["flds"].index(field_name)]

    @property
    def tags(self):
        return self.note.tags

    def has_tag(self, tag):
        return tag in self.note.tags

    def add_tag(self, tag):
        self.note.addTag(tag)

    def remove_tag(self, tag):
        self.note.delTag(tag)

    def is_due(self):
        return self.card.isDue

    @property
    def due_date(self):
        return self.card.due

    def save(self):
        self.note.flush()
        self.card.flush()

    def __str__(self):
        return f"AnkiCardWrapper(id: {self.id}, deck_id: {self.deck_id}, fields: {[repr(f) for f in self.fields]}, tags: {self.tags})"
