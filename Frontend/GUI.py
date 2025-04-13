import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "AI Assistant")  # Default name if not found
current_dir = os.getcwd()
TempDirectoryPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# Ensure directories exist
os.makedirs(TempDirectoryPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

# Constants
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
TOP_BAR_COLOR = "white"
TOP_BAR_TEXT_COLOR = "black"
SCROLLBAR_STYLESHEET = """
QScrollBar:vertical {
    border: none;
    background: black;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: white;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
}
"""

def AnswerModifier(Answer):
    """Removes empty lines from the answer."""
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    """Modifies the query to ensure it ends with a proper punctuation mark."""
    if not Query or not isinstance(Query, str):
        return ""

    Query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whom", "whose", "can you", "what's", "where's", "how's"]

    if any(word + " " in Query for word in question_words):
        if Query[-1] not in ['.', '?', '!']:
            Query += "?"
    else:
        if Query[-1] not in ['.', '?', '!']:
            Query += "."

    return Query.capitalize()

def SetMicrophoneStatus(Command):
    """Sets the microphone status in a file."""
    try:
        with open(os.path.join(TempDirectoryPath, 'Mic.data'), 'w', encoding='utf-8') as file:
            file.write(Command)
    except Exception as e:
        print(f"Error setting microphone status: {e}")

def GetMicrophoneStatus():
    """Retrieves the microphone status from a file."""
    try:
        with open(os.path.join(TempDirectoryPath, 'Mic.data'), 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error getting microphone status: {e}")
        return "False"

def SetAssistantStatus(Status):
    """Sets the assistant status in a file."""
    try:
        with open(os.path.join(TempDirectoryPath, 'Status.data'), 'w', encoding='utf-8') as file:
            file.write(Status)
    except Exception as e:
        print(f"Error setting assistant status: {e}")

def GetAssistantStatus():
    """Retrieves the assistant status from a file."""
    try:
        with open(os.path.join(TempDirectoryPath, 'Status.data'), 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error getting assistant status: {e}")
        return ""

def ShowTextToScreen(Text):
    """Writes text to a file for display on the screen."""
    try:
        with open(os.path.join(TempDirectoryPath, 'Responses.data'), "w", encoding='utf-8') as file:
            file.write(Text)
    except Exception as e:
        print(f"Error writing text to screen: {e}")

class ChatSection(QWidget):
    """Widget for displaying chat messages."""
    def __init__(self):
        super().__init__()
        self.old_chat_message = ""  # Track the last displayed message
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        # Chat text area
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        layout.addWidget(self.chat_text_edit)

        # GIF label
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(os.path.join(GraphicsDirPath, 'Jarvis.gif'))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        # Status label
        self.label = QLabel(" ")
        self.label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        # Timer for updating messages and status
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_messages)
        self.timer.timeout.connect(self.speech_recog_text)
        self.timer.start(100)  # Update every 100ms

    def load_messages(self):
        """Loads messages from the file and displays them in the chat window."""
        try:
            with open(os.path.join(TempDirectoryPath, 'Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()

                if messages and messages != self.old_chat_message:
                    self.add_message(messages, TEXT_COLOR)
                    self.old_chat_message = messages
        except Exception as e:
            print(f"Error loading messages: {e}")

    def speech_recog_text(self):
        """Updates the status label with the assistant's status."""
        try:
            status = GetAssistantStatus()
            self.label.setText(status)
        except Exception as e:
            print(f"Error updating status: {e}")

    def add_message(self, message, color):
        """Adds a message to the chat window with the specified color."""
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    """Initial screen with a GIF and microphone icon."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # GIF label
        gif_label = QLabel()
        movie = QMovie(os.path.join(GraphicsDirPath, 'Jarvis.gif'))
        movie.setScaledSize(QSize(800, 450))  # Adjust size as needed
        gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(gif_label, alignment=Qt.AlignCenter)

        # Microphone icon
        self.icon_label = QLabel()
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        # Status label
        self.label = QLabel("")
        self.label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 16px;")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # Timer for updating status
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.speech_recog_text)
        self.timer.start(100)

    def toggle_icon(self, event=None):
        """Toggles the microphone icon and updates the status."""
        if self.toggled:
            self.load_icon(os.path.join(GraphicsDirPath, 'Mic_off.png'))
            SetMicrophoneStatus("False")
        else:
            self.load_icon(os.path.join(GraphicsDirPath, 'Mic_on.png'))
            SetMicrophoneStatus("True")
        self.toggled = not self.toggled

    def load_icon(self, path):
        """Loads and scales an icon."""
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio)
        self.icon_label.setPixmap(pixmap)

    def speech_recog_text(self):
        """Updates the status label with the assistant's status."""
        try:
            status = GetAssistantStatus()
            self.label.setText(status)
        except Exception as e:
            print(f"Error updating status: {e}")

class CustomTopBar(QWidget):
    """Custom top bar with Home, Chat, Minimize, Maximize, and Close buttons."""
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setStyleSheet(f"background-color: black; color: {TOP_BAR_TEXT_COLOR};")
        layout = QHBoxLayout(self)  # Use QHBoxLayout for horizontal arrangement
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)  # Adjust spacing between buttons

        # Assistant Name
        assistant_name_label = QLabel(Assistantname)
        assistant_name_label.setStyleSheet(f"color: white; font-size: 18px;")
        layout.addWidget(assistant_name_label)

        # Stretch to align buttons to the center
        layout.addStretch(1)

        # Home and Chat Buttons
        home_button = QPushButton("Home")
        home_button.setIcon(QIcon(os.path.join(GraphicsDirPath, 'Home.png')))
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        home_button.setStyleSheet("border: none; color: black;")

        chat_button = QPushButton("Chat")
        chat_button.setIcon(QIcon(os.path.join(GraphicsDirPath, 'Chats.png')))
        chat_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        chat_button.setStyleSheet("border: none; color: black;")

        layout.addWidget(home_button)
        layout.addWidget(chat_button)

        # Stretch to push remaining buttons to the right
        layout.addStretch(1)

        # Minimize, Maximize, and Close Buttons
        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(os.path.join(GraphicsDirPath, 'Minimize2.png')))
        minimize_button.clicked.connect(self.parent().showMinimized)
        minimize_button.setStyleSheet("border: none;")

        maximize_button = QPushButton()
        maximize_button.setIcon(QIcon(os.path.join(GraphicsDirPath, 'Maximize.png')))
        maximize_button.clicked.connect(self.toggle_maximize)
        maximize_button.setStyleSheet("border: none;")

        close_button = QPushButton()
        close_button.setIcon(QIcon(os.path.join(GraphicsDirPath, 'Close.png')))
        close_button.clicked.connect(self.parent().close)
        close_button.setStyleSheet("border: none;")

        layout.addWidget(minimize_button)
        layout.addWidget(maximize_button)
        layout.addWidget(close_button)

    def toggle_maximize(self):
        """Toggles between maximized and normal window state."""
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

class MainWindow(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        # Stacked widget for switching between screens
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        chat_screen = ChatSection()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(chat_screen)

        # Custom top bar
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)

        # Set window size and style
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        # Set central widget
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    """Entry point for the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()