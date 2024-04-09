from db import DatabaseManager
from datetime import datetime, timedelta
from tkinter import messagebox

class FlashcardManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_deck_id = self.db.get_latest_deck_id()

    def create_deck(self, name):
        deck_id = self.db.add_deck(name)
        self.set_current_deck(deck_id)
        return deck_id

    def add_flashcard(self, question, answer):
        if self.current_deck_id is not None:
            self.db.add_flashcard(question, answer, self.current_deck_id)
        else:
            messagebox.showerror("Error", "No deck selected. Please create or select a deck first.")

    def get_random_flashcard(self):
        if self.current_deck_id is not None:
            return self.db.get_random_flashcard(self.current_deck_id)
        else:
            return None

    def get_next_flashcard(self):
        """
        Get the next flashcard to review from the current deck based on the spaced repetition algorithm
        """
        if self.current_deck_id is None:
            return None

        # Fetch all cards from the current deck
        cards = self.db.get_cards_from_deck(self.current_deck_id)  # Assuming this method returns a list of cards

        if not cards:
            return None

        # Sort the cards based on the next review date and pick the first one
        cards.sort(key=lambda card: card['next_review_date'])
        next_card = cards[0]

        return next_card

    def set_current_deck(self, deck_id):
        self.current_deck_id = deck_id

    def get_deck_info(self):
        # Placeholder for a method that fetches deck's detailed info, including name and remaining reviews
        if self.current_deck_id is not None:
            return self.db.get_deck_info(self.current_deck_id)  # Assuming this method returns a dict with deck info
        return None

    def get_card_data(self, card_id):
        if self.current_deck_id is None:
            return None
        return self.db.get_full_card_data(card_id)

    def super_memo(self, card_id, q):
        """
        SuperMemo 2 algorithm for spaced repetition learning
        :param card_id: ID of the flashcard
        :param q: User grade
        """
        # Fetch card data from the database
        card_data = self.db.get_card_data(card_id)  # Assuming this method returns a dict with card data

        n = card_data['repetition']
        EF = card_data['easiness_factor']
        I = card_data['interval']

        if q >= 3:  # Correct response
            if n == 0:
                I = 1
            elif n == 1:
                I = 6
            else:
                I = round(I * EF)
            n += 1
        else:  # Incorrect response
            n = 0
            I = 1

        EF = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        if EF < 1.3:
            EF = 1.3

        # Calculate the next review date
        next_review_date = datetime.now() + timedelta(days=I)

        # Update the card data in the database
        self.db.update_card_data(card_id, n, EF, I, next_review_date)  # Assuming this method updates the card data in the database

        return n, EF, I, next_review_date

    def update_card_schedule(self, card_id, difficulty):
        """
        Update the card schedule based on the user's response
        :param card_id: ID of the flashcard
        :param difficulty: User's response difficulty level
        """
        difficulty_map = {
            'easy': 5,
            'hard': 3,
            'very hard': 2,
            'again': 0
        }
        q = difficulty_map.get(difficulty, 0)
        self.super_memo(card_id, q)

    def delete_card(self, card_id):
        self.db.delete_card(card_id)

    def update_card(self, card_id, question, answer):
        self.db.update_card(card_id, question, answer)
