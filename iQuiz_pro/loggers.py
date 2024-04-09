import logging
import argparse
from termcolor import colored


class LevelColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        "DEBUG": "blue",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "magenta",
    }

    def format(self, record):
        record.combined_info = f"[{record.filename}:{record.lineno}]"
        levelname = record.levelname
        levelname_color = self.LEVEL_COLORS.get(levelname, "white")
        record.levelname = colored(levelname, levelname_color)
        log_message = super().format(record)
        record.levelname = levelname
        return log_message



db_logger = logging.getLogger("requests")
db_logger.setLevel(logging.DEBUG)

if not db_logger.handlers:
    db_console_handler = logging.StreamHandler()
    db_console_handler.setLevel(logging.DEBUG)
    db_formatter = LevelColoredFormatter("%(levelname)s - %(message)s - %(combined_info)s")
    db_console_handler.setFormatter(db_formatter)
    db_logger.propagate = False
    db_logger.addHandler(db_console_handler)

parser = argparse.ArgumentParser(
    description="Run the server with optional debug mode.")
parser.add_argument("--debug", action="store_true", help="Run in debug mode")
parser.add_argument("--encrypt", action="store_true", help="Encrypt the files")
args = parser.parse_args()

if args.debug:
    db_logger.setLevel(logging.DEBUG)
elif args.encrypt:
    db_logger.setLevel(logging.CRITICAL)
else:
    db_logger.setLevel(logging.INFO)