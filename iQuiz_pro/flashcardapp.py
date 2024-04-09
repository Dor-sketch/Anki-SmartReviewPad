"""
This file contains the main application logic for the flashcard app.
"""
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFont, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QVBoxLayout, QWidget, QSizePolicy, QHBoxLayout, \
    QInputDialog, QScrollArea, QTableWidget, QTableWidgetItem
import signal
import sys
from flashcardmanager import FlashcardManager
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

import sys
from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget, QLabel
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor


class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iQuiz Pro")
        self.manager = FlashcardManager()
        self.decks = self.manager.db.get_decks()
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.create_main_menu()

        # Set minimum size of the window
        self.setMinimumSize(800, 600)  # Set the minimum size to 800x600 pixels

        # Set initial window opacity to 0 (invisible)
        self.setWindowOpacity(0.0)

        # Create animation for window opacity
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(2000)  # Duration in milliseconds
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def load_stylesheet(self):
        # ...
        with open('style.css', 'r') as f:
            return f.read()

    def create_main_menu(self):
        self.clear_layout(self.main_layout)
        self.deck_label = QLabel(
            "Current Deck: No deck selected" if not self.manager.current_deck_id else "Current Deck: " + self.manager.get_deck_info()['name'])
        self.deck_label.setAlignment(Qt.AlignCenter)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(5, 5)
        effect.setColor(QColor(0, 0, 0, 50))
        self.deck_label.setGraphicsEffect(effect)


        self.main_layout.addWidget(self.deck_label)
        # Display the number of cards in the deck
        num_cards = len(self.manager.db.get_cards_from_deck(
            self.manager.current_deck_id))
        num_cards_label = QLabel(f"Number of cards in deck: {num_cards}")
        num_cards_label.setAlignment(Qt.AlignCenter)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(5, 5)
        effect.setColor(QColor(0, 0, 0, 50))
        num_cards_label.setGraphicsEffect(effect)
        self.main_layout.addWidget(num_cards_label)
        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()

        create_deck_button = self.create_button(
            "New", self.create_deck)
        create_deck_button.setShortcut(QKeySequence("1"))
        button_layout.addWidget(create_deck_button)

        select_deck_button = self.create_button(
            "Decks", self.select_deck)
        select_deck_button.setShortcut(QKeySequence("2"))
        button_layout.addWidget(select_deck_button)

        show_all_cards_button = self.create_button(
            "Cards", self.show_all_cards)
        show_all_cards_button.setShortcut(QKeySequence("3"))
        button_layout.addWidget(show_all_cards_button)

        add_flashcard_button = self.create_button(
            "Add", self.add_flashcard_view)
        add_flashcard_button.setShortcut(QKeySequence("4"))
        button_layout.addWidget(add_flashcard_button)

        review_flashcards_button = self.create_button(
            "Review", self.review_flashcards)
        review_flashcards_button.setShortcut(QKeySequence("5"))
        button_layout.addWidget(review_flashcards_button)
        button_layout.setSpacing(0)

        # Add the button layout to the main layout
        self.main_layout.addLayout(button_layout)

    def show_all_cards(self):
        self.clear_layout(self.main_layout)

        # Create a table widget with columns for each attribute of a card
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["Question", "Answer", "Next Review Date", "Actions"])
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(5, 5)
        effect.setColor(QColor(0, 0, 0, 50))
        table.setGraphicsEffect(effect)
        # make it stretch to the full width
        table.horizontalHeader().setStretchLastSection(True)
        cards = self.manager.db.get_cards_from_deck(
            self.manager.current_deck_id)
        if cards:
            table.setRowCount(len(cards))
            for i, card in enumerate(cards):
                table.setItem(i, 0, QTableWidgetItem(card['question']))
                table.setItem(i, 1, QTableWidgetItem(card['answer']))
                table.setItem(i, 2, QTableWidgetItem(
                    str(card['next_review_date'])))

                # Add buttons for editing and deleting
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda: self.edit_card(card['id']))
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(
                    lambda: self.delete_card(card['id']))

                table.setCellWidget(i, 3, edit_button)
                table.setCellWidget(i, 4, delete_button)

            # Sort by columns when headers are clicked
            table.horizontalHeader().sectionClicked.connect(table.sortByColumn)

            # Add the table to a scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(table)

            self.main_layout.addWidget(scroll_area)

            # Add a return button
            return_button = QPushButton("Return")
            return_button.clicked.connect(self.create_main_menu)
            self.main_layout.addWidget(return_button)
        else:
            QMessageBox.information(
                self, "Info", "No flashcards available in the current deck. Please add some first.")
            self.create_main_menu()

    # Add these methods to handle editing and deleting cards
    def edit_card(self, card_id):
        self.clear_layout(self.main_layout)

        card = self.manager.get_card_data(card_id)

        question_entry = QLineEdit(card['question'])
        answer_entry = QLineEdit(card['answer'])

        self.main_layout.addWidget(
            QLabel("Edit Flashcard", font=QFont('Helvetica', 18, QFont.Bold)))
        self.main_layout.addWidget(question_entry)
        self.main_layout.addWidget(answer_entry)

        button = QPushButton("Save")
        button.clicked.connect(lambda: self.save_card(
            card_id, question_entry.text(), answer_entry.text(), editing=True))
        self.main_layout.addWidget(button)

        return_button = QPushButton("Return to Main Menu")
        return_button.clicked.connect(self.create_main_menu)
        self.main_layout.addWidget(return_button)

    def save_card(self, card_id, question, answer, editing=False):
        if question and answer:
            self.manager.update_card(card_id, question, answer)
            QMessageBox.information(
                self, "Success", "Flashcard updated successfully!")
            if editing:
                self.show_all_cards()
            else:
                self.create_main_menu()
        else:
            QMessageBox.critical(
                self, "Error", "Question and answer cannot be empty.")

    def delete_card(self, card_id):
        print(f'card question: {self.manager.get_card_data(card_id)}')
        reply = QMessageBox.question(self, "Delete Flashcard", "Are you sure you want to delete this flashcard?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.manager.delete_card(card_id)
            QMessageBox.information(
                self, "Success", "Flashcard deleted successfully!")
            self.show_all_cards()

    def create_button(self, text, command):
        button = QPushButton(text)
        button.clicked.connect(command)
        self.main_layout.addWidget(button)
        return button

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            if child.layout():
                self.clear_layout(child.layout())

    def create_deck(self):
        deck_name, ok = QInputDialog.getText(
            self, "Create Deck", "Enter name of the new deck:")
        if ok:
            self.manager.create_deck(deck_name)
            QMessageBox.information(
                self, "Success", f"Deck '{deck_name}' created and selected.")
            self.update_deck_label()

    def select_deck(self):
        self.update_decks()

        deck_names = [deck['name'] for deck in self.decks]

        selected_deck_name, ok = QInputDialog.getItem(
            self, "Select a Deck", "Choose a deck:", deck_names, editable=False)
        if ok:
            selected_deck = next(
                (deck for deck in self.decks if deck['name'] == selected_deck_name), None)
            if selected_deck:
                self.manager.set_current_deck(selected_deck['id'])
                self.update_deck_label()
                QMessageBox.information(
                    self, "Success", f"Deck '{selected_deck_name}' selected.")

    def update_deck_label(self):
        deck_info = self.manager.get_deck_info()
        if deck_info:
            self.deck_label.setText(f"Current Deck: {deck_info['name']}")
        else:
            self.deck_label.setText("Current Deck: No deck selected")

    def add_flashcard_view(self):
        self.clear_layout(self.main_layout)

        self.question_entry = QLineEdit()
        self.answer_entry = QLineEdit()
        label = QLabel("Add a New Flashcard", font=QFont('Helvetica', 18, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(5, 5)
        effect.setColor(QColor(0, 0, 0, 50))
        label.setGraphicsEffect(effect)
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(self.question_entry)
        self.main_layout.addWidget(self.answer_entry)


        button = QPushButton("Submit")
        button.clicked.connect(self.save_flashcard)
        self.main_layout.addWidget(button)

        return_button = QPushButton("Return")
        return_button.clicked.connect(self.create_main_menu)
        self.main_layout.addWidget(return_button)

        # Ensure the widget and its children are shown
        self.show()

        # Set focus to the question entry field after a delay
        QTimer.singleShot(0, self.question_entry.setFocus)

    def save_flashcard(self):
        question = self.question_entry.text()
        answer = self.answer_entry.text()
        if question and answer:
            self.manager.add_flashcard(question, answer)
            QMessageBox.information(
                self, "Success", "Flashcard added successfully!")
            # ask user if they want to add another flashcard
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowTitle("Add Another Flashcard")
            msgBox.setText("Do you want to add another flashcard?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.Yes)
            reply = msgBox.exec_()
            if reply == QMessageBox.Yes:
                self.add_flashcard_view()
                # Set focus to the question entry field
                self.question_entry.setFocus()
            else:
                self.create_main_menu()
        else:
            QMessageBox.critical(
                self, "Error", "Question and answer cannot be empty.")

    def review_flashcards(self):
        self.clear_layout(self.main_layout)
        card = self.manager.get_next_flashcard()

        if card:
            label = QLabel(card['question'])
            label.setFont(QFont('Helvetica', 18, QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(10)
            effect.setOffset(5, 5)
            effect.setColor(QColor(0, 0, 0, 50))
            label.setGraphicsEffect(effect)
            self.main_layout.addWidget(label)
            show_answer_button = QPushButton("Answer")

            show_answer_button.clicked.connect(lambda: self.show_answer(card))
            # bind to space key as well
            show_answer_button.setShortcut(Qt.Key_Space)
            self.main_layout.addWidget(show_answer_button)
            skip_button = QPushButton("Skip")
            skip_button.clicked.connect(self.review_flashcards)
            self.main_layout.addWidget(skip_button)
            # bind to enter key as well
            skip_button.setShortcut(Qt.Key_Return)

            return_button = QPushButton("Return to Main Menu")
            return_button.clicked.connect(self.create_main_menu)
            self.main_layout.addWidget(return_button)

        else:
            QMessageBox.information(
                self, "Info", "No flashcards available in the current deck. Please add some first.")
            self.create_main_menu()

    def show_answer(self, card):
        self.clear_layout(self.main_layout)
        label = QLabel(card['answer'], wordWrap=True)
        label.setAlignment(Qt.AlignCenter)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(15)
        effect.setOffset(5, 5)
        effect.setColor(QColor(0, 0, 0, 50))
        label.setGraphicsEffect(effect)
        self.main_layout.addWidget(label)

        # Create a new QHBoxLayout for the buttons
        button_layout = QHBoxLayout()

        easy_button = self.create_button(
            "Easy", lambda: self.update_card_schedule(card['id'], 'easy'))
        hard_button = self.create_button(
            "Hard", lambda: self.update_card_schedule(card['id'], 'hard'))
        very_hard_button = self.create_button(
            "Very Hard", lambda: self.update_card_schedule(card['id'], 'very hard'))
        again_button = self.create_button(
            "Again", lambda: self.update_card_schedule(card['id'], 'again'))

        # Add the buttons to the button layout
        button_layout.addWidget(easy_button)
        button_layout.addWidget(hard_button)
        button_layout.addWidget(very_hard_button)
        button_layout.addWidget(again_button)

        # Add the button layout to the main layout
        self.main_layout.addLayout(button_layout)

        # Bind easy to 1, hard to 2, very hard to 3, again to 4
        easy_button.setShortcut(QKeySequence("1"))
        hard_button.setShortcut(QKeySequence("2"))
        very_hard_button.setShortcut(QKeySequence("3"))
        again_button.setShortcut(QKeySequence("4"))

        # Place buttons next to each other
        easy_button.setSizePolicy(QSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed))
        hard_button.setSizePolicy(QSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed))
        very_hard_button.setSizePolicy(QSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed))
        again_button.setSizePolicy(QSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed))

    def update_card_schedule(self, card_id, difficulty):
        self.manager.update_card_schedule(card_id, difficulty)
        self.review_flashcards()

    def update_decks(self):
        self.decks = self.manager.db.get_decks()

    def create_deck(self):
        deck_name, ok = QInputDialog.getText(
            self, "Create Deck", "Enter name of the new deck:")
        if ok:
            self.manager.create_deck(deck_name)
            QMessageBox.information(
                self, "Success", f"Deck '{deck_name}' created and selected.")
            self.update_deck_label()
            self.update_decks()

    def select_deck(self):
        self.update_decks()

        deck_names = [deck['name'] for deck in self.decks]

        selected_deck_name, ok = QInputDialog.getItem(
            self, "Select a Deck", "Choose a deck:", deck_names, editable=False)
        if ok:
            selected_deck = next(
                (deck for deck in self.decks if deck['name'] == selected_deck_name), None)
            if selected_deck:
                self.manager.set_current_deck(selected_deck['id'])
                self.update_deck_label()
                QMessageBox.information(
                    self, "Success", f"Deck '{selected_deck_name}' selected.")

    def update_deck_label(self):
        deck_info = self.manager.get_deck_info()
        if deck_info:
            self.deck_label.setText(f"Current Deck: {deck_info['name']}")
        else:
            self.deck_label.setText("Current Deck: No deck selected")


if __name__ == "__main__":
    # This line allows Ctrl+C to properly quit the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication([])
    window = FlashcardApp()
    window.setStyleSheet(window.load_stylesheet())
    window.show()
    sys.exit(app.exec_())
