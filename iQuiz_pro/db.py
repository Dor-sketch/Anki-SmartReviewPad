import sqlite3
from datetime import datetime
import uuid
import os

DB_FILE = "flashcards.db"
from loggers import db_logger  # Ensure your logging setup is correct

class DatabaseManager:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        if not os.path.exists(self.db_file):
            db_logger.warning("Database file not found. Creating new database file.")
        self.conn = self._connect_to_db()
        self._create_tables()

    def _connect_to_db(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # Enables column access by name
        return conn

    def update_card_data(self, card_id, review_count, easiness_factor, interval, next_review_date):
        try:
            last_reviewed_at = datetime.now()
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE flashcards
                SET ReviewCount = ?, EasinessFactor = ?, Interval = ?,
                    NextReviewDate = ?, LastReviewedAt = ?
                WHERE ID = ?
                """, (review_count, easiness_factor, interval, next_review_date, last_reviewed_at, card_id))
            self.conn.commit()
            db_logger.info(f"Card {card_id} updated with new data.")
        except sqlite3.Error as e:
            db_logger.error(f"Failed to update card data: {e}")
        finally:
            cursor.close()

    def _create_tables(self):
        try:
            cursor = self.conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS decks (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS flashcards (
                    ID TEXT PRIMARY KEY,
                    DeckID INTEGER NOT NULL,
                    Question TEXT NOT NULL,
                    Answer TEXT NOT NULL,
                    ReviewCount INTEGER DEFAULT 0,
                    LastReviewedAt DATETIME,
                    EasinessFactor REAL DEFAULT 2.5,
                    Interval INTEGER DEFAULT 1,
                    NextReviewDate DATETIME,
                    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (DeckID) REFERENCES decks(ID) ON DELETE CASCADE
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            db_logger.error(f"Database error: {e}")
        finally:
            cursor.close()

    def get_cards_from_deck(self, deck_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT ID, Question, Answer, NextReviewDate, ReviewCount FROM flashcards WHERE DeckID = ?", (deck_id,))
            cards = [{"id": row["ID"], "question": row["Question"], "answer": row["Answer"], "next_review_date": row["NextReviewDate"], "repetition": row["ReviewCount"]} for row in cursor.fetchall()]
            return cards
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch cards from deck {deck_id}: {e}")
            return []
        finally:
            cursor.close()

    def get_latest_deck_id(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT ID FROM decks ORDER BY CreatedAt DESC LIMIT 1")
            row = cursor.fetchone()
            return row["ID"] if row else None
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch latest deck ID: {e}")
            return None
        finally:
            cursor.close()

    def delete_card(self, card_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM flashcards WHERE ID = ?", (card_id,))
            self.conn.commit()
            db_logger.info(f"Card {card_id} deleted.")
        except sqlite3.Error as e:
            db_logger.error(f"Failed to delete card: {e}")
        finally:
            cursor.close()

    def update_card_review_data(self, card_id, review_count, next_review_date):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE flashcards
                SET ReviewCount = ?, NextReviewDate = ?
                WHERE ID = ?
                """, (review_count, next_review_date, card_id))
            self.conn.commit()
            db_logger.info(f"Card {card_id} review data updated.")
        except sqlite3.Error as e:
            db_logger.error(f"Failed to update card review data: {e}")
        finally:
            cursor.close()

    def update_card(self, card_id, question, answer):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE flashcards
                SET Question = ?, Answer = ?
                WHERE ID = ?
                """, (question, answer, card_id))
            self.conn.commit()
            db_logger.info(f"Card {card_id} updated.")
        except sqlite3.Error as e:
            db_logger.error(f"Failed to update card: {e}")
        finally:
            cursor.close()

    def get_card_data(self, card_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT ReviewCount AS repetition, EasinessFactor, Interval
                FROM flashcards WHERE ID = ?
                """, (card_id,))
            row = cursor.fetchone()
            return {"repetition": row["repetition"], "easiness_factor": row["EasinessFactor"], "interval": row["Interval"]}
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch card data: {e}")
            return None
        finally:
            cursor.close()

    def get_full_card_data(self, card_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT ReviewCount AS repetition, EasinessFactor, Interval, NextReviewDate, LastReviewedAt, CreatedAt, Question, Answer
                FROM flashcards WHERE ID = ?
                """, (card_id,))
            row = cursor.fetchone()
            return {"repetition": row["repetition"], "easiness_factor": row["EasinessFactor"], "interval": row["Interval"],
                    "next_review_date": row["NextReviewDate"], "last_reviewed_at": row["LastReviewedAt"],
                    "created_at": row["CreatedAt"], "question": row["Question"], "answer": row["Answer"]}
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch full card data: {e}")
            return None

    def add_deck(self, name):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO decks (Name) VALUES (?)", (name,))
            deck_id = cursor.lastrowid
            self.conn.commit()
            db_logger.info(f"Deck '{name}' added with ID {deck_id}")
            return deck_id
        except sqlite3.Error as e:
            db_logger.error(f"Failed to add deck: {e}")
            return None

    def add_flashcard(self, question, answer, deck_id):
        flashcard_id = str(uuid.uuid4())
        next_review_date = datetime.now()  # Set the next review date to the current date and time
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO flashcards (ID, DeckID, Question, Answer, LastReviewedAt, CreatedAt, EasinessFactor, Interval, NextReviewDate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (flashcard_id, deck_id, question, answer, None, datetime.now(), 2.5, 1, next_review_date))
            self.conn.commit()
            db_logger.info(f"Flashcard {flashcard_id} added to deck {deck_id}.")
        except sqlite3.Error as e:
            db_logger.error(f"Failed to add flashcard: {e}")
        finally:
            cursor.close()
    def get_random_flashcard(self, deck_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT Question, Answer FROM flashcards
                WHERE DeckID = ? ORDER BY RANDOM() LIMIT 1
                """, (deck_id,))
            flashcard = cursor.fetchone()
            return {"question": flashcard["Question"], "answer": flashcard["Answer"]} if flashcard else None
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch a random flashcard from deck {deck_id}: {e}")
            return None
        finally:
            cursor.close()

    def get_decks(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT ID, Name FROM decks")
            decks = [{"id": row["ID"], "name": row["Name"]} for row in cursor.fetchall()]
            return decks
        except sqlite3.Error as e:
            db_logger.error("Failed to fetch decks: " + str(e))
            return []
        finally:
            cursor.close()

    def get_deck_info(self, deck_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT Name FROM decks WHERE ID = ?", (deck_id,))
            row = cursor.fetchone()
            return {"id": deck_id, "name": row["Name"]} if row else None
        except sqlite3.Error as e:
            db_logger.error("Failed to fetch deck info: " + str(e))
            return None
        finally:
            cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
