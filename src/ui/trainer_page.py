from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QLineEdit, QComboBox
from PySide6.QtCore import Qt, QTimer
from logic.flashcard import FlashCard

class TrainerPage(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app  # Zugriff auf die Haupt-App
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. Navigation Header
        nav = QHBoxLayout()
        self.btn_back = QPushButton("⬅ Menü")
        
        self.direction_combo = QComboBox()
        # Die Items werden später über die Haupt-App (load_settings) gefüllt
        
        self.btn_settings = QPushButton("⚙")
        
        nav.addWidget(self.btn_back)
        nav.addStretch()
        nav.addWidget(self.direction_combo)
        nav.addWidget(self.btn_settings)
        layout.addLayout(nav)

        # 2. Modus-Switcher (Flashcard vs. Schreiben)
        modes = QHBoxLayout()
        self.btn_flash_mode = QPushButton("Karteikarten")
        self.btn_input_mode = QPushButton("Schreiben")
        modes.addWidget(self.btn_flash_mode)
        modes.addWidget(self.btn_input_mode)
        layout.addLayout(modes)

        # 3. Der Trainer Stack (Wechselt zwischen Karte und Eingabefeld)
        self.trainer_stack = QStackedWidget()
        
        # Sub-Page: Flashcard
        self.flashcard_widget = FlashCard()
        self.trainer_stack.addWidget(self.flashcard_widget)

        # Sub-Page: Input-Prüfung
        input_container = QWidget()
        ic_layout = QVBoxLayout(input_container)
        self.label_frage = QLabel("Übersetze:")
        self.label_wort = QLabel("-")
        self.label_wort.setStyleSheet("font-size: 24pt; font-weight: bold; margin: 20px;")
        self.label_wort.setAlignment(Qt.AlignCenter)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Deine Antwort...")
        self.label_result = QLabel("")
        self.label_result.setAlignment(Qt.AlignCenter)
        
        ic_layout.addWidget(self.label_frage)
        ic_layout.addWidget(self.label_wort)
        ic_layout.addWidget(self.input_field)
        ic_layout.addWidget(self.label_result)
        ic_layout.addStretch()
        
        self.trainer_stack.addWidget(input_container)
        layout.addWidget(self.trainer_stack)

    # Diese Methode wird von der main.py aufgerufen, um die Ansicht zu füllen
    def set_task(self, wort, loesung, direction_text):
        self.label_wort.setText(wort)
        self.flashcard_widget.setTexts(wort, loesung)
        self.label_frage.setText(f"Übersetze auf {direction_text}:")