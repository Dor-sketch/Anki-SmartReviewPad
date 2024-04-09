from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import sys
import signal
from flashcardapp import FlashcardApp

ALIGNE_RIGHT = False

def main():
    # This line allows Ctrl+C to properly quit the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    if ALIGNE_RIGHT:
        app.setLayoutDirection(Qt.RightToLeft)
    window = FlashcardApp()

    window.setStyleSheet(window.load_stylesheet())
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()