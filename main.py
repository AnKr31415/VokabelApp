from PySide6.QtWidgets import(
    QApplication, QLabel, QVBoxLayout, QWidget,
    QLineEdit, QPushButton, QListWidget,
    QStackedWidget, QMessageBox,
    QHBoxLayout, QSizePolicy, QComboBox
)
from PySide6.QtCore import Qt, QTimer

import sys
import database
from flashcard import FlashCard      # neu

class VokabelApp(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vokabel-App")
        self.resize(500, 560)
        
        # Intelligent Training Variablen
        self.current_vokabel_id = None
        self.current_englisch = ""

        # stylesheet laden
        self.setStyleSheet("""
        QWidget { background:#f5f5f5; font: 10pt "Segoe UI"; }
        QPushButton { background:#0078d7; color:white; border:none;
                      padding:6px 12px; border-radius:4px; }
        QPushButton:hover { background:#005a9e; }
        QLineEdit { padding:4px; border:1px solid #bbb; border-radius:2px; }
        QListWidget { background:white; border:1px solid #ccc; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12,12,12,12)
        main_layout.setSpacing(8)

        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        # Seite 1
        page1 = QWidget()
        self.pages.addWidget(page1)
        form = QVBoxLayout(page1)
        form.setSpacing(6)

        header1 = QHBoxLayout()
        header1.addStretch()
        self.button_next1 = QPushButton("Zur Seite 2")  # <- self. hinzufügen
        self.button_next1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        header1.addWidget(self.button_next1)
        form.addLayout(header1)

        form.addWidget(QLabel("Neue Vokabel"))
        self.de_input = QLineEdit()
        self.de_input.setPlaceholderText("Deutsch")
        form.addWidget(self.de_input)
        self.en_input = QLineEdit()
        self.en_input.setPlaceholderText("Englisch")
        form.addWidget(self.en_input)

        self.save_button = QPushButton("Speichern")
        form.addWidget(self.save_button)

        self.list_widget = QListWidget()
        form.addWidget(self.list_widget)

        self.save_button.clicked.connect(self.save_vokabel)
        self.list_widget.itemClicked.connect(self.show_delete_or_difficulty)

        self.load_vokabeln()

        # Button-Verbindung hinzufügen
        self.button_next1.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.button_next1.clicked.connect(self.switch_to_flashcard)

        # Seite 2
        page2 = QWidget()
        self.pages.addWidget(page2)
        layout2 = QVBoxLayout(page2)

        # Kopfzeile mit Headline und Button
        header_top = QHBoxLayout()
        headline = QLabel("Vokabeltrainer", alignment=Qt.AlignCenter)
        headline.setStyleSheet("font-size:20pt; font-weight:bold;")
        header_top.addWidget(headline, 1)
        
        self.button_next2 = QPushButton("Zur Seite 1")
        self.button_next2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        header_top.addWidget(self.button_next2)
        layout2.addLayout(header_top)

        # Umschalter zwischen Flashcard und Eingabe-Modus
        mode_buttons = QHBoxLayout()
        self.btn_flashcard_mode = QPushButton("Flashcard-Modus")
        self.btn_input_mode = QPushButton("Eingabe-Modus")
        self.btn_flashcard_mode.setStyleSheet("background:#0078d7; color:white;")
        mode_buttons.addWidget(self.btn_flashcard_mode)
        mode_buttons.addWidget(self.btn_input_mode)
        layout2.addLayout(mode_buttons)

        # StackedWidget für die beiden Modi
        self.trainer_stack = QStackedWidget()
        layout2.addWidget(self.trainer_stack, 1)

        # --- Mode 1: Flashcard ---
        flashcard_page = QWidget()
        flashcard_layout = QVBoxLayout(flashcard_page)
        self.card = FlashCard()
        flashcard_layout.addWidget(self.card, 1)
        self.trainer_stack.addWidget(flashcard_page)

        # --- Mode 2: Eingabe & Prüfen ---
        input_page = QWidget()
        input_layout = QVBoxLayout(input_page)
        
        self.label_frage = QLabel("Wie heißt das auf Englisch?")
        input_layout.addWidget(self.label_frage)
        
        self.label_deutsch = QLabel()
        self.label_deutsch.setStyleSheet("font-size:18pt; padding:12px;")
        input_layout.addWidget(self.label_deutsch)
        
        self.input_englisch = QLineEdit()
        self.input_englisch.setPlaceholderText("Englische Übersetzung eingeben...")
        input_layout.addWidget(self.input_englisch)
        self.input_englisch.returnPressed.connect(self.check_input_vokabel)  # Enter-Taste verbindet mit Prüfen
        
        self.btn_check = QPushButton("Prüfen")
        input_layout.addWidget(self.btn_check)
        
        self.label_result = QLabel()
        self.label_result.setStyleSheet("font-size:12pt; padding:12px;")
        self.label_result.setMinimumHeight(50)          # <- Mindesthöhe setzen
        self.label_result.setWordWrap(True)             # <- Zeilenumbruch
        self.label_result.setAlignment(Qt.AlignCenter) # <- Text zentrieren
        input_layout.addWidget(self.label_result)
        
        input_layout.addStretch()
        self.trainer_stack.addWidget(input_page)

        # Verbindungen
        self.card.known.connect(self.on_card_swiped)
        self.btn_flashcard_mode.clicked.connect(self.switch_to_flashcard)
        self.btn_input_mode.clicked.connect(self.switch_to_input)
        self.btn_check.clicked.connect(self.check_input_vokabel)
        self.button_next2.clicked.connect(lambda: self.pages.setCurrentIndex(0))

        self._show_random_card()

    def save_vokabel(self):
        deutsch = self.de_input.text()
        englisch = self.en_input.text()

        if deutsch and englisch:
            database.add_vocabel(deutsch, englisch)
            self.de_input.clear()
            self.en_input.clear()
            self.load_vokabeln()

    def load_vokabeln(self):
        self.list_widget.clear()
        vokabeln = database.get_all_vocabeln()

        for vok_id, de, en in vokabeln:
            item = self.list_widget.addItem(f"{de} → {en}")
            # id als Nutzerdaten speichern
            list_item = self.list_widget.item(self.list_widget.count()-1)
            list_item.setData(Qt.UserRole, vok_id)

    def show_delete_or_difficulty(self, item):
        """Zeigt Menü: Schwierigkeit setzen oder löschen"""
        vok_id = item.data(Qt.UserRole)
        deutsch_englisch = item.text()
        
        reply = QMessageBox.question(
            self,
            "Vokabel verwalten",
            f"»{deutsch_englisch}«\n\n"
            "[Yes] Schwierigkeit setzen\n"
            "[No] Löschen",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.set_difficulty_dialog(vok_id)
        else:
            database.delete_vokabel(vok_id)
            self.load_vokabeln()
    
    def set_difficulty_dialog(self, vok_id):
        """Dialog zum Setzen der Schwierigkeit (1-5)"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Schwierigkeit setzen")
        msg.setText("Wie schwierig ist diese Vokabel für dich?\n"
                   "1 = Kann ich kaum\n"
                   "2 = Schwer\n"
                   "3 = Mittel\n"
                   "4 = Leicht\n"
                   "5 = Kann ich sehr gut")
        
        # Combo-Box hinzufügen
        combo = QComboBox()
        combo.addItems(["1", "2", "3", "4", "5"])
        combo.setCurrentText("3")  # Standard = Mittel
        msg.layout().addWidget(combo)
        
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        if msg.exec() == QMessageBox.Ok:
            difficulty = int(combo.currentText())
            database.set_vocabel_difficulty(vok_id, difficulty)
            self.load_vokabeln()

    
    def _show_random_card(self):
        vok = database.get_smart_vocabel()
        if vok:
            self.current_vokabel_id = vok[0]  # Speichere die ID
            self.card.setTexts(vok[1], vok[2])
        else:
            self.current_vokabel_id = None
            self.card.setTexts("– keine Vokabeln –", "")
        self.card.setFocus()  # <- Focus auf Karte setzen

    def on_card_swiped(self, knows: bool):
        """Speichert Ergebnis und lädt nächste Vokabel"""
        if self.current_vokabel_id:
            # True = rechts gewischt (kennt), False = links gewischt (kennt nicht)
            database.update_vocabel_result(self.current_vokabel_id, knows)
        
        self._show_random_card()

    def switch_to_flashcard(self):
        self.trainer_stack.setCurrentIndex(0)
        self.btn_flashcard_mode.setStyleSheet("background:#0078d7; color:white;")
        self.btn_input_mode.setStyleSheet("")
        self.card.setFocus()
        self._show_random_card()

    def switch_to_input(self):
        self.trainer_stack.setCurrentIndex(1)
        self.btn_input_mode.setStyleSheet("background:#0078d7; color:white;")
        self.btn_flashcard_mode.setStyleSheet("")
        self.input_englisch.setFocus()
        self._show_random_card_input()

    def _show_random_card_input(self):
        vok = database.get_smart_vocabel()
        if vok:
            self.current_vokabel_id = vok[0]  # Speichere die ID
            self.label_deutsch.setText(vok[1])
            self.current_englisch = vok[2]
        else:
            self.current_vokabel_id = None
            self.label_deutsch.setText("– keine Vokabeln –")
            self.current_englisch = ""
        self.input_englisch.clear()
        self.label_result.clear()  # <- erst hier clearen, nach Verzögerung

    def check_input_vokabel(self):
        eingabe = self.input_englisch.text().strip()
        is_correct = eingabe.lower() == self.current_englisch.lower()
        
        # Speichere Ergebnis
        if self.current_vokabel_id:
            database.update_vocabel_result(self.current_vokabel_id, is_correct)
        
        if is_correct:
            self.label_result.setText("✓ Richtig!")
            self.label_result.setStyleSheet(
                "background-color: #4CAF50; color: white; "
                "font-size: 14pt; font-weight: bold; padding: 15px; "
                "border-radius: 4px;"
            )
        else:
            self.label_result.setText(
                f"✗ Leider falsch, richtig wäre gewesen: {self.current_englisch}"
            )
            self.label_result.setStyleSheet(
                "background-color: #f44336; color: white; "
                "font-size: 12pt; padding: 15px; border-radius: 4px;"
            )
        self.input_englisch.clear()
        # verzögerte nächste Vokabel laden (z.B. nach 2 Sekunden)
        QTimer.singleShot(2000, self._show_random_card_input)

if __name__ == "__main__":
    database.init_db()
    database.migrate_db()  # <- Füge neue Spalten hinzu, falls nötig

    # optional, vor app = QApplication(...):
    QApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    QApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, True)

    app = QApplication(sys.argv)

    # externe Stylesheet‑Datei einlesen
    try:
        with open("style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Stylesheet load error:", e)

    window = VokabelApp()
    window.show()
    sys.exit(app.exec())