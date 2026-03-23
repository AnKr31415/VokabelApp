"""Debug-Version der App mit Print-Ausgaben"""
import sys
import database

# Enable debug mode
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

# Patch database functions with debug output
original_get_smart_vocabel = database.get_smart_vocabel
original_update_vocabel_result = database.update_vocabel_result

def debug_get_smart_vocabel():
    result = original_get_smart_vocabel()
    debug_print(f"get_smart_vocabel() -> {result}")
    return result

def debug_update_vocabel_result(vok_id, is_correct):
    debug_print(f"update_vocabel_result(id={vok_id}, correct={is_correct})")
    return original_update_vocabel_result(vok_id, is_correct)

database.get_smart_vocabel = debug_get_smart_vocabel
database.update_vocabel_result = debug_update_vocabel_result

# Jetzt die echte App importieren
from main import VokabelApp
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

database.init_db()
database.migrate_db()

app = QApplication(sys.argv)

try:
    with open("style.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
except Exception as e:
    print("Stylesheet load error:", e)

window = VokabelApp()

# Patch der on_card_swiped Methode für Debug
original_on_card_swiped = window.on_card_swiped
def debug_on_card_swiped(knows):
    debug_print(f"on_card_swiped(knows={knows}) aufgerufen")
    return original_on_card_swiped(knows)

window.on_card_swiped = debug_on_card_swiped
window.card.known.connect(window.on_card_swiped)

debug_print("App startet...")
window.show()

sys.exit(app.exec())
