from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QLineEdit, 
                             QComboBox, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from logic.flashcard import FlashCard

class TrainerPage(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app  
        
        # Schriften fixieren
        self.font_normal = QFont("Arial", 16)
        self.font_active = QFont("Arial", 22, QFont.Bold)
        
        # Styles zentral speichern
        self.style_normal_red = "color: red; border: 3px solid transparent;"
        self.style_normal_green = "color: green; border: 3px solid transparent;"
        
        self.init_ui()

    def init_ui(self):
        # Das Hauptlayout der Seite
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        # --- 1. Header (Wichtig für main.py) ---
        nav = QHBoxLayout()
        self.btn_back = QPushButton("⬅ Menü")
        self.direction_combo = QComboBox()
        self.btn_settings = QPushButton("⚙")
        nav.addWidget(self.btn_back)
        nav.addStretch()
        nav.addWidget(self.direction_combo)
        nav.addWidget(self.btn_settings)
        self.main_layout.addLayout(nav)

        # --- 2. Modus-Switcher ---
        modes = QHBoxLayout()
        self.btn_flash_mode = QPushButton("Karteikarten")
        self.btn_input_mode = QPushButton("Schreiben")
        modes.addWidget(self.btn_flash_mode)
        modes.addWidget(self.btn_input_mode)
        self.main_layout.addLayout(modes)

        # --- 3. Der Trainer Stack ---
        self.trainer_stack = QStackedWidget()
        self.main_layout.addWidget(self.trainer_stack)

        # --- SEITE 1: FLASHCARD BEREICH ---
        flash_page_widget = QWidget()
        flash_page_layout = QVBoxLayout(flash_page_widget)
        flash_page_layout.setContentsMargins(0, 0, 0, 0)

        # A: Die Karte (in einem eigenen Container, um Abstände zu garantieren)
        self.flashcard_widget = FlashCard()
        flash_page_layout.addWidget(self.flashcard_widget, stretch=5)

        # B: Die Feedback-Labels (In einem harten Rahmen am Boden)
        self.footer_frame = QFrame()
        self.footer_frame.setFrameShape(QFrame.NoFrame)
        self.footer_frame.setMinimumHeight(130) # MASSIV PLATZ RESERVIEREN
        self.footer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        footer_layout = QHBoxLayout(self.footer_frame)
        
        self.unknown_label = QLabel("Weiß ich nicht!")
        self.unknown_label.setFont(self.font_normal)
        self.unknown_label.setStyleSheet(self.style_normal_red)
        self.unknown_label.setAlignment(Qt.AlignCenter)
        self.unknown_label.setFixedSize(220, 100) # BREIT UND HOCH FIXIEREN

        self.known_label = QLabel("Weiß ich!")
        self.known_label.setFont(self.font_normal)
        self.known_label.setStyleSheet(self.style_normal_green)
        self.known_label.setAlignment(Qt.AlignCenter)
        self.known_label.setFixedSize(220, 100) # BREIT UND HOCH FIXIEREN

        footer_layout.addWidget(self.unknown_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.known_label)
        
        flash_page_layout.addWidget(self.footer_frame, stretch=1)
        self.trainer_stack.addWidget(flash_page_widget)

        # --- SEITE 2: SCHREIB MODUS ---
        input_page_widget = QWidget()
        input_layout = QVBoxLayout(input_page_widget)
        self.label_wort = QLabel("-")
        self.label_wort.setAlignment(Qt.AlignCenter)
        self.label_wort.setStyleSheet("font-size: 24pt; font-weight: bold;")
        self.input_field = QLineEdit()
        self.label_frage = QLabel("Übersetze:")
        self.label_result = QLabel("")
        input_layout.addWidget(self.label_frage)
        input_layout.addWidget(self.label_wort)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.label_result)
        input_layout.addStretch()
        self.trainer_stack.addWidget(input_page_widget)

    def set_task(self, wort, loesung, direction_text):
        """Reset-Funktion für neue Karten"""
        self.flashcard_widget.setTexts(wort, loesung)
        self.label_wort.setText(wort)
        
        # Reset der Optik (WICHTIG!)
        self.known_label.setFont(self.font_normal)
        self.unknown_label.setFont(self.font_normal)
        self.known_label.setStyleSheet(self.style_normal_green)
        self.unknown_label.setStyleSheet(self.style_normal_red)

    def highlight_label(self, is_known):
        """Wird von der main.py aufgerufen"""
        if is_known:
            self.known_label.setFont(self.font_active)
            self.known_label.setStyleSheet("color: green; border: 3px solid green; border-radius: 12px; background-color: #f0fff0;")
        else:
            self.unknown_label.setFont(self.font_active)
            self.unknown_label.setStyleSheet("color: red; border: 3px solid red; border-radius: 12px; background-color: #fff0f0;")