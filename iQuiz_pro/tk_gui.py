from tkinter import ttk
import tkinter as tk
from tkinter import simpledialog, messagebox
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk


class FlashcardApp:
    def __init__(self, master):

        self.master = master
        # Create a style
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", background="#eee", relief="raised")
        # make all center aligned
        style.configure("TLabel", anchor="center")
        self.manager = FlashcardManager()
        self.create_main_menu()
        self.decks = self.manager.db.get_decks()

    def create_main_menu(self):
        self.clear_frame()
        tk.Label(self.master, text="Flashcard Reviewer", font=('Helvetica', 18, 'bold')).pack(pady=20)
        self.deck_label = tk.Label(self.master, text= "Current Deck: No deck selected" if not self.manager.current_deck_id else "Current Deck: " + self.manager.get_deck_info()['name'])
        self.deck_label.pack(pady=5)
        tk.Button(self.master, text="Create Deck", command=self.create_deck, width=20).pack(pady=5)
        tk.Button(self.master, text="Select Deck", command=self.select_deck, width=20).pack(pady=5)
        tk.Button(self.master, text="Add Flashcard", command=self.add_flashcard_view, width=20).pack(pady=5)
        tk.Button(self.master, text="Review Flashcards", command=self.review_flashcards, width=20).pack(pady=5)

    def create_deck(self):
        deck_name = simpledialog.askstring("Create Deck", "Enter name of the new deck:")
        if deck_name:
            self.manager.create_deck(deck_name)
            messagebox.showinfo("Success", f"Deck '{deck_name}' created and selected.")
            self.update_deck_label()
    def select_deck(self):
        self.update_decks()  # Update the decks list

        deck_names = [deck['name'] for deck in self.decks]  # Define deck_names

        def on_ok():
            selected_deck_name = combo.get()
            selected_deck = next((deck for deck in self.decks if deck['name'] == selected_deck_name), None)
            if selected_deck:
                self.manager.set_current_deck(selected_deck['id'])
                self.update_deck_label()
                messagebox.showinfo("Success", f"Deck '{selected_deck_name}' selected.")
            dialog.destroy()

        dialog = tk.Toplevel(self.master)
        dialog.title("Select a Deck")
        tk.Label(dialog, text="Choose a deck:").pack()
        combo = ttk.Combobox(dialog, values=deck_names)
        combo.pack()
        tk.Button(dialog, text="OK", command=on_ok).pack()

    def update_deck_label(self):
        deck_info = self.manager.get_deck_info()
        if deck_info:
            self.deck_label.config(text=f"Current Deck: {deck_info['name']}")
        else:
            self.deck_label.config(text="Current Deck: No deck selected")



    def add_flashcard_view(self):
        self.clear_frame()
        tk.Label(self.master, text="Add a New Flashcard", font=('Helvetica', 18, 'bold')).pack(pady=20)

        question_frame = tk.Frame(self.master)
        tk.Label(question_frame, text="Question:").pack(side=tk.LEFT)
        self.question_entry = tk.Entry(question_frame)
        self.question_entry.pack()
        question_frame.pack(pady=5)

        answer_frame = tk.Frame(self.master)
        tk.Label(answer_frame, text="Answer:").pack(side=tk.LEFT)
        self.answer_entry = tk.Entry(answer_frame)
        self.answer_entry.pack()
        answer_frame.pack(pady=5)

        tk.Button(self.master, text="Submit", command=self.save_flashcard).pack(pady=20)

    def save_flashcard(self):
        question = self.question_entry.get()
        answer = self.answer_entry.get()
        if question and answer:
            self.manager.add_flashcard(question, answer)
            messagebox.showinfo("Success", "Flashcard added successfully!")
            self.create_main_menu()
        else:
            messagebox.showerror("Error", "Question and answer cannot be empty.")

    def review_flashcards(self):
        self.clear_frame()
        card = self.manager.get_next_flashcard()

        print(card)
        if card:
            ttk.Label(self.master, text="Question:", font=('Helvetica', 18, 'bold')).grid(row=0, column=0, columnspan=4, pady=20, sticky='nsew')
            ttk.Label(self.master, text=card['question'], wraplength=400).grid(row=1, column=0, columnspan=4, pady=10, sticky='nsew')
            show_answer_button = ttk.Button(self.master, text="Show Answer", command=lambda: self.show_answer(card))
            show_answer_button.grid(row=2, column=0, columnspan=4, pady=20, sticky='nsew')
            self.master.bind('<space>', lambda event: self.show_answer(card))
            skip_button = ttk.Button(self.master, text="Skip", command=self.review_flashcards)
            skip_button.grid(row=3, column=0, columnspan=4, pady=10, sticky='nsew')
            self.master.bind('<Return>', lambda event: self.review_flashcards())
        else:
            messagebox.showinfo("Info", "No flashcards available in the current deck. Please add some first.")
            self.create_main_menu()

    def show_answer(self, card):
        self.clear_frame()
        ttk.Label(self.master, text="Question:", font=('Helvetica', 18, 'bold')).grid(row=0, column=0, columnspan=4, pady=20, sticky='nsew')
        ttk.Label(self.master, text=card['question'], wraplength=400).grid(row=1, column=0, columnspan=4, pady=10, sticky='nsew')
        ttk.Label(self.master, text="Answer:", font=('Helvetica', 18, 'bold')).grid(row=2, column=0, columnspan=4, pady=20, sticky='nsew')
        ttk.Label(self.master, text=card['answer'], wraplength=400).grid(row=3, column=0, columnspan=4, pady=10, sticky='nsew')
        ttk.Button(self.master, text="Easy", command=lambda: self.update_card_schedule(card['id'], 'easy')).grid(row=4, column=0, pady=10, sticky='nsew')
        ttk.Button(self.master, text="Hard", command=lambda: self.update_card_schedule(card['id'], 'hard')).grid(row=4, column=1, pady=10, sticky='nsew')
        ttk.Button(self.master, text="Very Hard", command=lambda: self.update_card_schedule(card['id'], 'very hard')).grid(row=4, column=2, pady=10, sticky='nsew')
        ttk.Button(self.master, text="Again", command=lambda: self.update_card_schedule(card['id'], 'again')).grid(row=4, column=3, pady=10, sticky='nsew')
        self.master.bind('<space>', lambda event: self.update_card_schedule(card['id'], 'easy'))
        self.master.bind('1', lambda event: self.update_card_schedule(card['id'], 'easy'))
        self.master.bind('2', lambda event: self.update_card_schedule(card['id'], 'hard'))
        self.master.bind('3', lambda event: self.update_card_schedule(card['id'], 'very hard'))
        self.master.bind('4', lambda event: self.update_card_schedule(card['id'], 'again'))

    def update_card_schedule(self, card_id, difficulty):
        self.manager.update_card_schedule(card_id, difficulty)
        self.review_flashcards()


    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()


    def update_decks(self):
        self.decks = self.manager.db.get_decks()

    def create_deck(self):
        deck_name = simpledialog.askstring("Create Deck", "Enter name of the new deck:")
        if deck_name:
            self.manager.create_deck(deck_name)
            messagebox.showinfo("Success", f"Deck '{deck_name}' created and selected.")
            self.update_deck_label()
            self.update_decks()  # Update the decks list



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Flashcard Reviewer")
    root.geometry("500x300")
    app = FlashcardApp(root)
    root.mainloop()
