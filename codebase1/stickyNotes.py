# Import necessary PySide6 modules
# (QApplication, QMainWindow, QWidget, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QFont)
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QFont
import sys

# Create the StickyNote class (inherits from QWidget)
# This represents each individual sticky note window
class StickyNote(QWidget):

    # Initialize the note window
    # (set title, size, and create the layout)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sticky Note")
        self.setGeometry(100, 100, 300, 250)
    
    # Create the text area
    # (use QTextEdit for multi-line editable text)
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type your note here...")
    
    # Set font size for the text area
    # (create QFont object and set it to the text edit)
        font = QFont()
        font.setPointSize(50)
        self.text_edit.setFont(font)
    
    # Create color buttons
    # (create buttons for yellow, pink, green, blue)
        self.yellow_btn = QPushButton("Yellow")
        self.pink_btn = QPushButton("Pink")
        self.green_btn = QPushButton("Green")
        self.blue_btn = QPushButton("Blue")
    
    # Create delete button
        self.delete_btn = QPushButton("Delete")
    
    # Create horizontal layout for color buttons
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.yellow_btn)
        color_layout.addWidget(self.pink_btn)
        color_layout.addWidget(self.green_btn)
        color_layout.addWidget(self.blue_btn)
    
    # Create vertical layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addLayout(color_layout)
        layout.addWidget(self.delete_btn)
    
    # Set the layout
        self.setLayout(layout)
    
    # Method to change note color
        self.yellow_btn.clicked.connect(lambda: self.change_color("#FFFF99"))
        self.pink_btn.clicked.connect(lambda: self.change_color("#FFB6C1"))
        self.green_btn.clicked.connect(lambda: self.change_color("#90EE90"))
        self.blue_btn.clicked.connect(lambda: self.change_color("#ADD8E6"))
    
    # Method to close/delete the note
        self.delete_btn.clicked.connect(self.close)

    def change_color(self, color):
        self.setStyleSheet(f"background-color: {color};")


# Create the MainWindow class (inherits from QMainWindow)
# This is the main app window with the "Create New Note" button
class MainWindow(QMainWindow):

    # Initialize the main window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sticky Notes App")
        self.setGeometry(100, 100, 300, 150)
    
    # Create list to store note windows
        self.notes = []
    
    # Create the "Create New Note" button
        self.create_btn = QPushButton("Create New Note")
        self.create_btn.clicked.connect(self.create_note)
    
    # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.create_btn)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    # Method to create a new sticky note
    def create_note(self):
        note = StickyNote()
        note.show()
        self.notes.append(note)

# Create and run the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())