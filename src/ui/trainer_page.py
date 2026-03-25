from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QLineEdit, QComboBox, QFrame
from PySide6.QtCore import Qt, QTimer
from logic.flashcard import FlashCard

class TrainerPage(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app  
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. Navigation Header (unverändert)
        nav = QHBoxLayout()
        self.btn_back = QPushButton("⬅ Menü")
        self.direction_combo = QComboBox()
        self.btn_settings = QPushButton("⚙")
        nav.addWidget(self.btn_back)
        nav.addStretch()
        nav.addWidget(self.direction_combo)
        nav.addWidget(self.btn_settings)
        layout.addLayout(nav)

        # 2. Modus-Switcher (unverändert)
        modes = QHBoxLayout()
        self.btn_flash_mode = QPushButton("Karteikarten")
        self.btn_input_mode = QPushButton("Schreiben")
        modes.addWidget(self.btn_flash_mode)
        modes.addWidget(self.btn_input_mode)
        layout.addLayout(modes)

        # 3. Der Trainer Stack
        self.trainer_stack = QStackedWidget()
        
        # Sub-Page: Flashcard
        self.flashcard_widget = FlashCard()
        self.trainer_stack.addWidget(self.flashcard_widget)

        # Sub-Page: Input-Prüfung
        input_container = QWidget()
        ic_layout = QVBoxLayout(input_container)
        
        self.label_frage = QLabel("Übersetze:")
        self.label_wort = QLabel("-")
        self.label_wort.setStyleSheet("font-size: 24pt; font-weight: bold; margin-top: 10px;")
        self.label_wort.setAlignment(Qt.AlignCenter)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Deine Antwort...")
        
        self.label_result = QLabel("")
        self.label_result.setAlignment(Qt.AlignCenter)

        # --- NEU: KI HILFE BEREICH ---
        self.ai_section = QFrame()
        self.ai_section.setObjectName("ai_section") # Für QSS Styling
        ai_layout = QVBoxLayout(self.ai_section)
        
        self.label_sentence = QLabel("Lade Beispielsatz...")
        self.label_sentence.setWordWrap(True)
        self.label_sentence.setStyleSheet("color: #555; font-style: italic;")
        
        self.label_mnemonic = QLabel("Lade Eselsbrücke...")
        self.label_mnemonic.setWordWrap(True)
        self.label_mnemonic.setStyleSheet("color: #2c3e50; font-weight: bold;")
        
        ai_layout.addWidget(self.label_sentence)
        ai_layout.addWidget(self.label_mnemonic)
        # --- ENDE KI HILFE BEREICH ---
        
        ic_layout.addWidget(self.label_frage)
        ic_layout.addWidget(self.label_wort)
        ic_layout.addWidget(self.input_field)
        ic_layout.addWidget(self.label_result)
        ic_layout.addWidget(self.ai_section) # KI Bereich unter das Resultat
        ic_layout.addStretch()
        
        self.trainer_stack.addWidget(input_container)
        layout.addWidget(self.trainer_stack)

    def set_task(self, wort, loesung, direction_text):
        self.label_wort.setText(wort)
        self.flashcard_widget.setTexts(wort, loesung)
        self.label_frage.setText(f"Übersetze auf {direction_text}:")
        
        # KI-Texte zurücksetzen, damit der alte Satz nicht bei der neuen Vokabel steht
        self.label_sentence.setText("KI generiert Kontext...")
        self.label_mnemonic.setText("KI sucht Eselsbrücke...")