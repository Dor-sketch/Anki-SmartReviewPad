import logging
import subprocess


class GlobalStrikeCounter:
    _instance = None

    def __new__(cls):
        logging.info("Initializing GlobalStrikeCounter")
        if cls._instance is None:
            logging.info("Creating new instance of GlobalStrikeCounter")
            cls._instance = super(GlobalStrikeCounter, cls).__new__(cls)
            cls._instance.strike_count = 0
        else:
            logging.info("Returning existing instance of GlobalStrikeCounter, current strike count: {}".format(
                cls._instance.strike_count))
        return cls._instance

    def increment(self):
        self.strike_count += 1
        self.check_for_special_effects()

    def reset(self):
        self.strike_count = 0
        self.play_sound_with_notification("Basso", "Anki", "Incorrect answer!")

    def check_for_special_effects(self):
        if self.strike_count % 5 == 0:
            self.apply_five_strike_effect()
        if self.strike_count % 10 == 0:
            self.apply_ten_strike_effect()
        else:
            self.play_correct_answer_sound("Glass")

    def apply_five_strike_effect(self):
        self.play_correct_answer_sound("Hero")

    def apply_ten_strike_effect(self):
        self.play_correct_answer_sound("Basso")

    def play_correct_answer_sound(self, sound_name):
        try:
            subprocess.run(
                ["osascript", "-e", 'display notification "Correct answer!" with title "Anki" subtitle "Good job! Current streak: {}" sound name "{}"'.format(self.strike_count, sound_name)])
        except Exception as e:
            print(f"Couldn't play sound: {e}")

    def play_sound_with_notification(self, sound_name, notification_title, notification_subtitle):
        try:
            subprocess.run(["osascript", "-e", 'display notification "{}" with title "{}" subtitle "{}" sound name "{}"'.format(
                notification_subtitle, notification_title, notification_subtitle, sound_name)])
        except Exception as e:
            print(f"Couldn't play sound: {e}")

    def __str__(self):
        return str(self.strike_count)
