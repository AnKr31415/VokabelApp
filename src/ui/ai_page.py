from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFrame
from PySide6.QtCore import Qt

class AIPage(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header mit Zurück-Button
        nav = QHBoxLayout()
        self.btn_back = QPushButton("⬅ Menü")
        nav.addWidget(self.btn_back)
        nav.addStretch()
        layout.addLayout(nav)

        # Titel
        title = QLabel("KI Eselsbrücken-Generator")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Eingabe-Bereich
        input_box = QGroupBox("Welches Wort bereitet dir Kopfzerbrechen?")
        ib_layout = QVBoxLayout(input_box)
        
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("z.B. 'environment' oder 'l'écureuil'")
        self.btn_generate = QPushButton("✨ Eselsbrücke erzeugen")
        self.btn_generate.setStyleSheet("background-color: #9b59b6; color: white; height: 40px;")
        
        ib_layout.addWidget(self.word_input)
        ib_layout.addWidget(self.btn_generate)
        layout.addWidget(input_box)

        # Ergebnis-Anzeige
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("Hier erscheint deine Merkhilfe...")
        self.result_display.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 10px;")
        layout.addWidget(self.result_display)

from PySide6.QtWidgets import QGroupBox # Oben importieren falls nötig