from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QListWidget
from PySide6.QtCore import Qt

class ManagementPage(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app # Zugriff auf Haupt-App (Datenbank/Navigation)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        self.btn_back = QPushButton("⬅ Hauptmenü")
        layout.addWidget(self.btn_back)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Meine Vokabeln</b>", styleSheet="font-size: 18pt;"))
        header.addStretch()
        
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setFixedSize(40, 40)
        
        self.btn_train = QPushButton("Üben ➔")
        self.btn_train.setObjectName("primaryButton")
        
        header.addWidget(self.btn_settings)
        header.addWidget(self.btn_train)
        layout.addLayout(header)

        # Input Card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        
        row = QHBoxLayout()
        self.de_input = QLineEdit()
        self.en_input = QLineEdit()
        row.addWidget(self.de_input)
        row.addWidget(self.en_input)
        card_layout.addLayout(row)

        self.btn_add = QPushButton("Vokabel hinzufügen")
        self.btn_add.setObjectName("primaryButton")
        card_layout.addWidget(self.btn_add)
        layout.addWidget(card)

        # Legende für Schwierigkeit
        legend_frame = QFrame()
        legend_layout = QHBoxLayout(legend_frame)

        legend_layout.addWidget(QLabel("<b>Schwierigkeit:</b>"))

        legend_layout.addWidget(QLabel("★☆☆☆☆ = sehr schwer"))
        legend_layout.addWidget(QLabel("★★☆☆☆ = schwer"))
        legend_layout.addWidget(QLabel("★★★☆☆ = mittel"))
        legend_layout.addWidget(QLabel("★★★★☆ = leicht"))
        legend_layout.addWidget(QLabel("★★★★★ = sehr leicht"))

        legend_layout.addStretch()

        layout.addWidget(legend_frame)

        # Liste
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.btn_import = QPushButton("Excel Import")
        layout.addWidget(self.btn_import)