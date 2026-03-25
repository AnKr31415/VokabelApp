from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

class SettingsPage(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Einstellungen</b>", styleSheet="font-size: 16pt;"))
        
        self.source_combo = QComboBox()
        self.target_combo = QComboBox()
        langs = ["Deutsch", "Englisch", "Französisch", "Spanisch"]
        self.source_combo.addItems(langs)
        self.target_combo.addItems(langs)
        
        layout.addWidget(QLabel("Deine Sprache:"))
        layout.addWidget(self.source_combo)
        layout.addWidget(QLabel("Lernsprache:"))
        layout.addWidget(self.target_combo)
        
        btn_layout = QHBoxLayout()
        self.btn_back = QPushButton("Abbrechen")
        self.btn_save = QPushButton("Speichern")
        self.btn_save.setObjectName("primaryButton")
        
        btn_layout.addWidget(self.btn_back)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)
        layout.addStretch()