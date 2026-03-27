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
from ui.vocab_item_widget import VocabItemWidget
from PySide6.QtWidgets import QListWidgetItem

import logic.ai_handler as ai_handler

from PySide6.QtWidgets import QSplashScreen,QApplication,QPushButton ,QStackedWidget, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtCore import QSize

from google import genai
import os
from dotenv import load_dotenv

class vocabelApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("vocabel-App Professional")
        self.resize(550, 650)
        
        # App-Status / Variablen
        self.current_vocabel_id = None
        self.current_target_text = ""
        self.direction = "source_to_target"
        
        # UI Setup
        self.init_ui()
        
        # Daten laden
        self.load_settings()
        self.load_vocabeln()
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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
        self.management_page.btn_add.clicked.connect(self.add_vocabel)
        self.management_page.btn_import.clicked.connect(self.import_excel)
        self.management_page.list_widget.itemClicked.connect(self.delete_vocabel_dialog)
        
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

        self.start_page.btn_train.clicked.connect(self.switch_to_trainer)

    
    # --- DATENBANK-FUNKTIONEN ---
    def add_vocabel(self):
        de = self.management_page.de_input.text().strip()
        en = self.management_page.en_input.text().strip()
        if de and en:
            database.add_vocabel(de, en)
            self.management_page.de_input.clear()
            self.management_page.en_input.clear()
            self.load_vocabeln()
            self.refresh_task()

    def load_vocabeln(self):
        """Lädt nur vocabeln, die in den gewählten Sprachen Werte haben."""
        self.management_page.list_widget.clear()

        # Aktuell ausgewählte Sprachen
        src = self.source_lang
        trg = self.target_lang

        # Alle vocabeln aus der Datenbank abrufen
        all_vocs = database.get_all_vocabeln()  # Liefert z.B. (id, de, en, fr, es, difficulty)

        for v in all_vocs:
            v_id = v[0]
            # Mapping der Sprachen auf die Werte der vocabel
            lang_map = {
                "Deutsch": v[1],
                "Englisch": v[2],
                "Französisch": v[3],
                "Spanisch": v[4]
            }

            # Überspringe vocabeln, die in einer der beiden aktiven Sprachen leer sind
            if not lang_map[src] or not lang_map[trg]:
                continue

            # Schwierigkeit abrufen, falls vorhanden
            difficulty = v[5] if len(v) > 5 else 3

            # Nur die Texte der aktiven Sprachen an das Widget übergeben
            src_text = lang_map[src]
            trg_text = lang_map[trg]

            # Neues Listenelement erstellen
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 90))  # Höhe der Box

            # vocabel-Widget erstellen
            widget = VocabItemWidget(v_id, src_text, trg_text, difficulty, self)

            # Widget in die Liste einfügen
            self.management_page.list_widget.addItem(item)
            self.management_page.list_widget.setItemWidget(item, widget)
                
    def delete_vocabel_dialog(self, item):
        v_id = item.data(Qt.UserRole)
        if QMessageBox.question(self, "Löschen", "vocabel wirklich löschen?") == QMessageBox.Yes:
            database.delete_vocabel(v_id)
            self.load_vocabeln()

    def set_vocabel_difficulty(self, vok_id, difficulty):
        database.set_vocabel_difficulty(vok_id, difficulty)

    def refresh_task(self):
        """Lädt die nächste vocabel für den Trainer in den aktiven Sprachen."""
        vok = database.get_smart_vocabel(source=self.source_lang, target=self.target_lang)
        if vok:
            self.current_vocabel_id = vok['id']

            src, trg = vok[self.source_lang], vok[self.target_lang]
            self.current_target_text = trg

            direction_label = self.target_lang if self.direction == "source_to_target" else self.source_lang
            self.trainer_page.set_task(src, trg, direction_label)


    def check_input(self):
        guess = self.trainer_page.input_field.text().strip().lower()
        correct = guess == self.current_target_text.lower()
        database.update_vocabel_result(self.current_vocabel_id, correct)
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
        # 1. Visuelles Feedback anzeigen
        self.trainer_page.highlight_label(known)

        # 2. Nach kurzer Zeit wieder zurücksetzen
        QTimer.singleShot(800, self.reset_label_styles)

        # 3. Ergebnis speichern
        database.update_vocabel_result(self.current_vocabel_id, known)

        # 4. Neue Aufgabe laden (leicht verzögert, damit man das Feedback sieht)
        QTimer.singleShot(800, self.refresh_task)

    def change_direction(self):
        self.direction = self.trainer_page.direction_combo.currentData() or "source_to_target"
        self.refresh_task()
    
    def reset_label_styles(self):
        self.trainer_page.known_label.setFont(self.trainer_page.font_normal)
        self.trainer_page.unknown_label.setFont(self.trainer_page.font_normal)
        self.trainer_page.known_label.setStyleSheet(self.trainer_page.style_normal_green)
        self.trainer_page.unknown_label.setStyleSheet(self.trainer_page.style_normal_red)

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

    def switch_to_trainer(self):
        self.pages.setCurrentIndex(2)
        self.setFocus()

    def flip(self):
        self.is_flipped = not self.is_flipped
        if self.is_flipped:
            self.label.setText(self.current_target_text)
        else:
            self.label.setText(self.current_source_text)

    def import_excel(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Excel wählen", "", "*.xlsx")
        if path:
            msg = database.import_from_excel(path)
            QMessageBox.information(self, "Import", msg)
            self.load_vocabeln()

    # In main.py

    def keyPressEvent(self, event):
        if self.pages.currentIndex() == 2: # Trainer-Seite
            if event.key() == Qt.Key_Right:
                self.trainer_page.highlight_label(True)
                # Wir geben Qt 200ms Zeit zum Zeichnen, bevor wir die Karte wechseln
                QTimer.singleShot(200, lambda: self.handle_swipe(True))
            
            elif event.key() == Qt.Key_Left:
                self.trainer_page.highlight_label(False)
                QTimer.singleShot(200, lambda: self.handle_swipe(False))

    def finish_task_animation(self, known):
        # Erst Labels zurücksetzen
        self.trainer_page.known_label.setStyleSheet(self.trainer_page.style_normal_green)
        self.trainer_page.unknown_label.setStyleSheet(self.trainer_page.style_normal_red)
        # Dann die nächste vocabel laden
        self.handle_swipe(known)

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

# --- DER ANGEPASSTE START-BLOCK ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. Splash Screen Setup
    # Du kannst hier ein QPixmap mit einem Logo laden: QPixmap("assets/logo.png")
    # Wenn du kein Bild hast, erstellt dieser Code ein einfaches graues Rechteck als Platzhalter:
    from PySide6.QtGui import QPixmap, QColor, QPainter
    
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(QColor("#2c3e50")) # Eine Farbe passend zu deinem App-Stil
    
    splash = QSplashScreen(splash_pix)
    splash.show()
    
    # 2. Feedback geben während des Ladens
    splash.showMessage("Initialisiere Datenbank...", Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, Qt.GlobalColor.white)
    app.processEvents() # Wichtig, damit das Fenster sofort zeichnet
    database.init_db()
    
    splash.showMessage("Lade UI-Komponenten...", Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, Qt.GlobalColor.white)
    app.processEvents()
    
    # 3. Das Hauptfenster erstellen (hier passiert deine ganze Logik)
    window = vocabelApp()
    
    splash.showMessage("App bereit!", Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, Qt.GlobalColor.white)
    app.processEvents()
    
    # 4. Splash Screen beenden und Fenster zeigen
    window.show()
    splash.finish(window) 
    
    sys.exit(app.exec())