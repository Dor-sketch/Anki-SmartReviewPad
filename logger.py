"""
This module contains the logger class for the Anki addon.
"""
import os
import logging
import re
import codecs


class AnkiAddonLogger:

    class LevelColoredFormatter(logging.Formatter):

        def format(self, record):
            record.combined_info = f"[{record.filename}:{record.lineno}]"
            levelname = record.levelname

            # Check if the message contains Unicode escape sequences for Hebrew
            if re.search(r'\\u05[0-9A-Fa-f]{2}', record.msg):
                record.msg = codecs.decode(record.msg, 'unicode_escape')

            log_message = super().format(record)
            record.levelname = levelname  # Resetting to original
            return log_message

    @classmethod
    def initialize_logging(cls):
        log_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'anki_addon.log')
        logging.basicConfig(filename=log_path,
                            filemode='a', level=logging.DEBUG)

        # Create and configure custom logger
        logger = logging.getLogger("anki_addon")

        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = cls.LevelColoredFormatter(
                "%(asctime)s %(combined_info)-20s [%(levelname)s] %(message)s"
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            logger.propagate = False


def initialize_logging():
    # Configure root logger to log to a file
    log_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'anki_addon.log')
    file_handler = logging.FileHandler(log_path, 'a', encoding='utf-8')

    file_handler.setLevel(logging.DEBUG)
    formatter = AnkiAddonLogger.LevelColoredFormatter(
        "%(asctime)s %(combined_info)-20s [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    # Configure your specific logger
    anki_addon_logger = logging.getLogger("anki_addon")
    anki_addon_logger.setLevel(logging.DEBUG)

    # Add the same file handler to your specific logger
    anki_addon_logger.addHandler(file_handler)
