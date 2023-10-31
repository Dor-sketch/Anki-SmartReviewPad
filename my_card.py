from aqt import mw
import logging
import os

def initialize_logging():
    log_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'anki_addon.log')
    logging.basicConfig(filename=log_path, filemode='a', level=logging.DEBUG)


class AnkiCardWrapper:
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

# # Example usage:
# card = mw.reviewer.card
# anki_card = AnkiCardWrapper(card)

# logging.debug("Card ID: %s", anki_card.id)
# logging.debug("Deck ID: %s", anki_card.deck_id)
# logging.debug("Fields: %s", anki_card.fields)
# logging.debug("Front Field: %s", anki_card.field('Front'))
# logging.debug("Has Tag 'Important': %s", anki_card.has_tag('Important'))


# # Uncomment to modify card and save
# # anki_card.add_tag("NewTag")
# # anki_card.save()

# logging.debug(anki_card)
