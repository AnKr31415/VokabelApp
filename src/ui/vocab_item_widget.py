from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class VocabItemWidget(QWidget):
    def __init__(self, vok_id, deutsch, englisch, difficulty, parent_app):
        super().__init__()
        self.vok_id = vok_id
        self.difficulty = difficulty
        self.app = parent_app

        self.setMinimumHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Vokabel Text groß darstellen
        self.label = QLabel(f"{deutsch}  →  {englisch}")
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setMinimumWidth(250)
        layout.addWidget(self.label)

        layout.addStretch()

        # Sterne Buttons
        star_container = QWidget()
        star_layout = QHBoxLayout(star_container)
        star_layout.setSpacing(6)
        star_layout.setContentsMargins(0, 0, 0, 0)

        self.star_buttons = []

        for i in range(1, 6):
            btn = QPushButton()
            btn.setFixedSize(36, 36)  # größeres Klickfeld
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFlat(True)
            btn.setText("☆")
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    font-size: 16pt;   /* Stern kleiner */
                    color: lightgray;
                    background: transparent;
                }
                QPushButton:hover {
                    color: gold;
                }
            """)
            btn.clicked.connect(lambda checked, level=i: self.set_difficulty(level))
            self.star_buttons.append(btn)
            star_layout.addWidget(btn)

        layout.addWidget(star_container)

        self.update_stars()

    def set_difficulty(self, level):
        self.difficulty = level
        self.update_stars()
        self.app.set_vocabel_difficulty(self.vok_id, level)

    def update_stars(self):
        for i, btn in enumerate(self.star_buttons, start=1):
            if i <= self.difficulty:
                btn.setText("★")
                btn.setStyleSheet("""
                    QPushButton {
                        border: none;
                        font-size: 16pt;
                        color: gold;
                        background: transparent;
                    }
                """)
            else:
                btn.setText("☆")
                btn.setStyleSheet("""
                    QPushButton {
                        border: none;
                        font-size: 16pt;
                        color: lightgray;
                        background: transparent;
                    }
                    QPushButton:hover {
                        color: gold;
                    }
                """)