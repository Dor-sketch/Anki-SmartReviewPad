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

    def remove_tag(self, card_id, tag):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM flashcard_tags
                WHERE FlashcardID = ? AND TagID = (
                    SELECT ID FROM tags WHERE Name = ?
                )
                """, (card_id, tag))
            self.conn.commit()
            db_logger.info(f"Tag '{tag}' removed from flashcard {card_id}")
        except sqlite3.Error as e:
            db_logger.error(f"Failed to remove tag from flashcard: {e}")
        finally:
            cursor.close()

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
                CREATE TABLE IF NOT EXISTS tags (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS flashcard_tags (
                    FlashcardID TEXT NOT NULL,
                    TagID INTEGER NOT NULL,
                    PRIMARY KEY (FlashcardID, TagID),
                    FOREIGN KEY (FlashcardID) REFERENCES flashcards(ID) ON DELETE CASCADE,
                    FOREIGN KEY (TagID) REFERENCES tags(ID) ON DELETE CASCADE
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            db_logger.error(f"Database error: {e}")
        finally:
            cursor.close()

    def get_tag_ids(self, tag_names):
        try:
            cursor = self.conn.cursor()
            tag_ids = []
            for tag_name in tag_names:
                cursor.execute("SELECT ID FROM tags WHERE Name = ?", (tag_name))
                row = cursor.fetchone()
                if row:
                    tag_ids.append(row["ID"])
                else:
                    tag_id = self.add_new_tag(tag_name)
                    if tag_id:
                        tag_ids.append(tag_id)
            return tag_ids
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch tag IDs: {e}")
            return []
        finally:
            cursor.close()

    def add_new_tag(self, tag_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO tags (Name) VALUES (?)", (tag_name))
            tag_id = cursor.lastrowid
            self.conn.commit()
            db_logger.info(f"Tag '{tag_name}' added with ID {tag_id}")
            return tag_id
        except sqlite3.Error as e:
            db_logger.error(f"Failed to add tag: {e}")
            return None
        finally:
            cursor.close()

    def add_tag_to_flashcard(self, flashcard_id, tag_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO flashcard_tags (FlashcardID, TagID) VALUES (?, ?)", (flashcard_id, tag_id))
            self.conn.commit()
            db_logger.info(f"Tag {tag_id} added to flashcard {flashcard_id}")
        except sqlite3.Error as e:
            db_logger.error(f"Failed to add tag to flashcard: {e}")
        finally:
            cursor.close()

    def get_tags_for_flashcard(self, flashcard_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT t.Name
                FROM tags t
                JOIN flashcard_tags ft ON t.ID = ft.TagID
                WHERE ft.FlashcardID = ?
                """, (flashcard_id,))
            tags = [row["Name"] for row in cursor.fetchall()]
            return tags
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch tags for flashcard: {e}")
            return []
        finally:
            cursor.close()

    def get_flashcards_with_tag(self, tag_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT f.ID, f.Question, f.Answer
                FROM flashcards f
                JOIN flashcard_tags ft ON f.ID = ft.FlashcardID
                JOIN tags t ON ft.TagID = t.ID
                WHERE t.Name = ?
                """, (tag_name,))
            flashcards = [{"id": row["ID"], "question": row["Question"], "answer": row["Answer"]} for row in cursor.fetchall()]
            return flashcards
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch flashcards with tag: {e}")
            return []
        finally:
            cursor.close()

    def get_tags(self, card_id=None):
        if card_id:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT t.Name
                    FROM tags t
                    JOIN flashcard_tags ft ON t.ID = ft.TagID
                    WHERE ft.FlashcardID = ?
                    """, (card_id,))
                tags = [row["Name"] for row in cursor.fetchall()]
                return tags
            except sqlite3.Error as e:
                db_logger.error(f"Failed to fetch tags for flashcard {card_id}: {e}")
                return []
            finally:
                cursor.close()
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT Name FROM tags")
            tags = [row["Name"] for row in cursor.fetchall()]
            return tags
        except sqlite3.Error as e:
            db_logger.error(f"Failed to fetch tags: {e}")
            return []
        finally:
            cursor.close()

    def set_tag(self, card_id, tag):
        if isinstance(tag, list):
            for t in tag:
                self._set_tag(card_id, t)
        else:
            self._set_tag(card_id, tag)

    def _set_tag(self, card_id, tag):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT ID FROM tags WHERE Name = ?", (tag,))
            row = cursor.fetchone()
            if row:
                tag_id = row["ID"]
            else:
                cursor.execute("INSERT INTO tags (Name) VALUES (?)", (tag,))
                tag_id = cursor.lastrowid
            cursor.execute("INSERT INTO flashcard_tags (FlashcardID, TagID) VALUES (?, ?)", (card_id, tag_id))
            self.conn.commit()
            db_logger.info(f"Tag '{tag}' set for flashcard {card_id}")
        except sqlite3.Error as e:
            db_logger.error(f"Failed to set tag for flashcard: {e}")
        finally:
            cursor.close()

    def get_cards_from_deck(self, deck_id, tag=None):
        if tag:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT f.ID, f.Question, f.Answer, f.NextReviewDate, f.ReviewCount
                    FROM flashcards f
                    JOIN flashcard_tags ft ON f.ID = ft.FlashcardID
                    JOIN tags t ON ft.TagID = t.ID
                    WHERE f.DeckID = ? AND t.Name = ?
                    """, (deck_id, tag))
                cards = [{"id": row["ID"], "question": row["Question"], "answer": row["Answer"], "next_review_date": row["NextReviewDate"], "repetition": row["ReviewCount"]} for row in cursor.fetchall()]
                return cards
            except sqlite3.Error as e:
                db_logger.error(f"Failed to fetch cards from deck {deck_id} with tag {tag}: {e}")
                return []
            finally:
                cursor.close()
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
