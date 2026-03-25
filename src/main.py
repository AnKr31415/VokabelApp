import sys
import os

# Den absoluten Pfad zum aktuellen Ordner (src) ermitteln
current_dir = os.path.dirname(os.path.abspath(__file__))

# Falls 'src' im Pfad ist, fügen wir es explizit hinzu
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Erst danach kommen deine Imports
import logic.database as database
from ui.management_page import ManagementPage
from ui.trainer_page import TrainerPage
from ui.settings_page import SettingsPage
from ui.ai_page import AIPage
from ui.start_page import StartPage

import logic.ai_handler as ai_handler

from PySide6.QtWidgets import QApplication,QPushButton ,QStackedWidget, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Qt, QTimer

from google import genai
import os
from dotenv import load_dotenv

class VokabelApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vokabel-App Professional")
        self.resize(550, 650)
        
        # App-Status / Variablen
        self.current_vokabel_id = None
        self.current_target_text = ""
        self.direction = "source_to_target"
        
        # UI Setup
        self.init_ui()
        
        # Daten laden
        self.load_settings()
        self.load_vokabeln()
        self.refresh_task()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.pages = QStackedWidget()
        self.main_layout.addWidget(self.pages)

        # Instanzen erstellen
        self.start_page = StartPage(self)        # Neuer Index 0
        self.management_page = ManagementPage(self)
        self.trainer_page = TrainerPage(self)
        self.settings_page = SettingsPage(self)
        self.ai_page = AIPage(self)

        # Dem Stack hinzufügen (Index wichtig!)
        self.pages.addWidget(self.start_page)      # 0
        self.pages.addWidget(self.management_page) # 1
        self.pages.addWidget(self.trainer_page)    # 2
        self.pages.addWidget(self.settings_page)   # 3
        self.pages.addWidget(self.ai_page)         # 4

        self.setup_connections()
        self.apply_styles()

    def apply_styles(self):
        """Lädt das Stylesheet"""
        qss_path = os.path.join(os.path.dirname(__file__), "ui", "style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())


    def setup_connections(self):
        """Verbindet alle Buttons der Startseite und der Unterseiten mit der Logik"""
        
        # --- 1. NAVIGATION VON DER STARTSEITE (Index 0) ---
        self.start_page.btn_manage.clicked.connect(lambda: self.pages.setCurrentIndex(1))   # Zu Management
        self.start_page.btn_train.clicked.connect(lambda: self.pages.setCurrentIndex(2))    # Zu Trainer
        self.start_page.btn_settings.clicked.connect(lambda: self.pages.setCurrentIndex(3)) # Zu Settings
        self.start_page.btn_ai.clicked.connect(lambda: self.pages.setCurrentIndex(4))       # Zu KI-Schmiede

        # --- 2. ZURÜCK-NAVIGATION (Alle führen zum Hauptmenü - Index 0) ---
        self.management_page.btn_back.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.trainer_page.btn_back.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.settings_page.btn_back.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.ai_page.btn_back.clicked.connect(lambda: self.pages.setCurrentIndex(0))

        # --- 3. MANAGEMENT LOGIK ---
        self.management_page.btn_add.clicked.connect(self.add_vokabel)
        self.management_page.btn_import.clicked.connect(self.import_excel)
        self.management_page.list_widget.itemClicked.connect(self.delete_vokabel_dialog)
        
        # Optional: Shortcut von Management direkt zu Settings oder Trainer
        self.management_page.btn_settings.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        self.management_page.btn_train.clicked.connect(lambda: self.pages.setCurrentIndex(2))

        # --- 4. TRAINER LOGIK ---
        self.trainer_page.direction_combo.currentTextChanged.connect(self.change_direction)
        self.trainer_page.btn_flash_mode.clicked.connect(lambda: self.trainer_page.trainer_stack.setCurrentIndex(0))
        self.trainer_page.btn_input_mode.clicked.connect(lambda: self.trainer_page.trainer_stack.setCurrentIndex(1))
        self.trainer_page.input_field.returnPressed.connect(self.check_input)
        self.trainer_page.flashcard_widget.known.connect(self.handle_swipe)
        
        # Shortcut vom Trainer zu Settings
        self.trainer_page.btn_settings.clicked.connect(lambda: self.pages.setCurrentIndex(3))

        # --- 5. KI-GENERATOR LOGIK (Standalone Seite) ---
        self.ai_page.btn_generate.clicked.connect(self.run_ai_generator)

        # --- 6. SETTINGS LOGIK ---
        self.settings_page.btn_save.clicked.connect(self.save_settings)
    
    # --- DATENBANK-FUNKTIONEN ---
    def add_vokabel(self):
        de = self.management_page.de_input.text().strip()
        en = self.management_page.en_input.text().strip()
        if de and en:
            database.add_vocabel(de, en)
            self.management_page.de_input.clear()
            self.management_page.en_input.clear()
            self.load_vokabeln()
            self.refresh_task()

    def load_vokabeln(self):
        self.management_page.list_widget.clear()
        for v_id, de, en in database.get_all_vocabeln():
            item = self.management_page.list_widget.addItem(f"{de} ➔ {en}")

    def delete_vokabel_dialog(self, item):
        v_id = item.data(Qt.UserRole)
        if QMessageBox.question(self, "Löschen", "Vokabel wirklich löschen?") == QMessageBox.Yes:
            database.delete_vokabel(v_id)
            self.load_vokabeln()

    def refresh_task(self):
        vok = database.get_smart_vocabel()
        if vok:
            self.current_vokabel_id = vok[0]
            # Bestimme Quell- und Zielwort
            src, trg = (vok[1], vok[2]) if self.direction == "source_to_target" else (vok[2], vok[1])
            self.current_target_text = trg
            
            # --- KI LOGIK START ---
            # Wir holen uns Hilfe für das Zielwort
            ai_data = ai_handler.get_ai_support(trg, self.target_lang)
            
            if ai_data:
                sentence = ai_data.get('sentence', '')
                mnemonic = ai_data.get('mnemonic', '')
                # Du musst in deiner TrainerPage entsprechende Labels haben:
                self.trainer_page.label_sentence.setText(f"Kontext: {sentence}")
                self.trainer_page.label_mnemonic.setText(f"Tipp: {mnemonic}")
            # --- KI LOGIK ENDE ---

            direction_label = self.target_lang if self.direction == "source_to_target" else self.source_lang
            self.trainer_page.set_task(src, trg, direction_label)

    def check_input(self):
        guess = self.trainer_page.input_field.text().strip().lower()
        correct = guess == self.current_target_text.lower()
        database.update_vocabel_result(self.current_vokabel_id, correct)
        self.trainer_page.label_result.setText("✓ Richtig!" if correct else f"✗ Falsch: {self.current_target_text}")
        self.trainer_page.label_result.setStyleSheet("color: green;" if correct else "color: red;")
        QTimer.singleShot(1500, self.next_task_input)

    def run_ai_generator(self):
        """Logik für die Standalone KI-Seite"""
        wort = self.ai_page.word_input.text().strip()
        
        if not wort:
            self.ai_page.result_display.setText("Bitte gib zuerst ein Wort ein!")
            return
            
        # UI Feedback geben
        self.ai_page.result_display.setText("Gemini 3.1 Flash-Lite denkt nach... 🧠")
        self.ai_page.btn_generate.setEnabled(False) # Button sperren während der Anfrage
        
        # Die Sprache aus den Settings holen
        ziel_sprache = self.target_lang if hasattr(self, 'target_lang') else "Englisch"
        
        # KI-Abfrage über den ai_handler
        ai_data = ai_handler.get_ai_support(wort, ziel_sprache)
        
        if ai_data:
            sentence = ai_data.get('sentence', 'Kein Beispielsatz gefunden.')
            mnemonic = ai_data.get('mnemonic', 'Keine Eselsbrücke gefunden.')
            
            # Ergebnis schön formatiert anzeigen
            ergebnis_text = f"Wort: {wort}\n"
            ergebnis_text += f"{'='*20}\n\n"
            ergebnis_text += f"Beispielsatz:\n{sentence}\n\n"
            ergebnis_text += f"Eselsbrücke (Tipp):\n{mnemonic}"
            
            self.ai_page.result_display.setText(ergebnis_text)
        else:
            self.ai_page.result_display.setText("Fehler: Die KI konnte nicht erreicht werden. Prüfe dein Internet oder das API-Limit.")
            
        self.ai_page.btn_generate.setEnabled(True) # Button wieder freigeben

    def next_task_input(self):
        self.trainer_page.label_result.setText("")
        self.trainer_page.input_field.clear()
        self.refresh_task()

    def handle_swipe(self, known):
        database.update_vocabel_result(self.current_vokabel_id, known)
        self.refresh_task()

    def change_direction(self):
        self.direction = self.trainer_page.direction_combo.currentData() or "source_to_target"
        self.refresh_task()

    def load_settings(self):
        self.source_lang = database.get_setting('source_language', 'Deutsch')
        self.target_lang = database.get_setting('target_language', 'Englisch')
        self.trainer_page.direction_combo.clear()
        self.trainer_page.direction_combo.addItem(f"{self.source_lang} ➔ {self.target_lang}", "source_to_target")
        self.trainer_page.direction_combo.addItem(f"{self.target_lang} ➔ {self.source_lang}", "target_to_source")
        self.settings_page.source_combo.setCurrentText(self.source_lang)
        self.settings_page.target_combo.setCurrentText(self.target_lang)

    def save_settings(self):
        database.set_setting('source_language', self.settings_page.source_combo.currentText())
        database.set_setting('target_language', self.settings_page.target_combo.currentText())
        self.load_settings()
        QMessageBox.information(self, "Erfolg", "Gespeichert!")

    def import_excel(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Excel wählen", "", "*.xlsx")
        if path:
            msg = database.import_from_excel(path)
            QMessageBox.information(self, "Import", msg)
            self.load_vokabeln()

    def generate_standalone_mnemonic(self):
        wort = self.ai_page.word_input.text().strip()
        if not wort:
            return
            
        self.ai_page.result_display.setText("Die KI denkt nach... 🧠")
        
        # Wir nutzen den vorhandenen ai_handler
        # Wir nehmen 'Englisch' als Standard-Zielsprache oder holen es aus den Settings
        ai_data = ai_handler.get_ai_support(wort, self.target_lang)
        
        if ai_data:
            text = f"Wort: {wort}\n\n"
            text += f"Beispielsatz:\n{ai_data.get('sentence', 'Kein Satz gefunden.')}\n\n"
            text += f"Eselsbrücke:\n{ai_data.get('mnemonic', 'Keine Hilfe gefunden.')}"
            self.ai_page.result_display.setText(text)
        else:
            self.ai_page.result_display.setText("Fehler: Konnte keine Verbindung zur KI herstellen.")

# --- DER START-BLOCK (Ganz wichtig!) ---
if __name__ == "__main__":
    database.init_db()
    app = QApplication(sys.argv)
    window = VokabelApp()
    window.show() # Ohne das bleibt das Fenster unsichtbar!
    sys.exit(app.exec())