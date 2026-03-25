from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt

class StartPage(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Titel & Willkommen
        self.label_title = QLabel("Vokabel Master Pro")
        self.label_title.setStyleSheet("font-size: 28pt; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        self.label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_title)

        self.label_subtitle = QLabel("Was möchtest du heute tun?")
        self.label_subtitle.setStyleSheet("font-size: 14pt; color: #7f8c8d;")
        self.label_subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_subtitle)

        # Container für die Menü-Buttons
        menu_frame = QFrame()
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setSpacing(15)

        # Die Haupt-Buttons
        self.btn_train = self.create_menu_button("🚀 Training starten", "#2ecc71")
        self.btn_manage = self.create_menu_button("📚 Vokabeln verwalten", "#3498db")
        self.btn_ai = self.create_menu_button("✨ KI Eselsbrücken", "#9b59b6")
        self.btn_settings = self.create_menu_button("⚙ Einstellungen", "#95a5a6")

        menu_layout.addWidget(self.btn_train)
        menu_layout.addWidget(self.btn_manage)
        menu_layout.addWidget(self.btn_ai)
        menu_layout.addWidget(self.btn_settings)

        layout.addWidget(menu_frame)
        layout.addStretch()

    def create_menu_button(self, text, color):
        btn = QPushButton(text)
        btn.setMinimumHeight(60)
        btn.setMinimumWidth(300)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 16pt;
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: white;
                color: {color};
                border: 2px solid {color};
            }}
        """)
        return btn