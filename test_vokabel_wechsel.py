#!/usr/bin/env python3
"""Test: Überprüfe ob die Vokabel-Änderung funktioniert"""
import sqlite3
import time

DB_NAME = "vokabeln.db"

# Funktion: Nachahmung von update_vocabel_result  
def update_vocabel_result_test(vok_id, is_correct):
    """Speichert Statistiken für eine Vokabel"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    current_time = time.time()
    
    if is_correct:
        cursor.execute("""
            UPDATE vokabeln 
            SET correct_count = correct_count + 1,
                total_attempts = total_attempts + 1,
                last_asked = ?,
                next_review = ?
            WHERE id = ?
        """, (current_time, current_time + 86400, vok_id))
    else:
        cursor.execute("""
            UPDATE vokabeln 
            SET incorrect_count = incorrect_count + 1,
                total_attempts = total_attempts + 1,
                last_asked = ?,
                next_review = ?
            WHERE id = ?
        """, (current_time, current_time + 300, vok_id))
    
    conn.commit()
    conn.close()

# Funktion: Nachahmung von get_smart_vocabel
def get_smart_vocabel_test():
    """Intelligente Auswahl der Vokabel"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    current_time = time.time()
    
    cursor.execute("""
        SELECT id, deutsch, englisch FROM vokabeln
        WHERE vokabeln.id > 0
        ORDER BY 
            (CASE 
                WHEN last_asked > (? - 20) THEN -999.0      
                WHEN last_asked > (? - 120) THEN -100.0     
                WHEN last_asked > (? - 300) THEN -50.0      
                ELSE 0
            END) +
            (CASE 
                WHEN last_asked = 0 OR total_attempts = 0 THEN 100.0
                ELSE 0
            END) +
            (CASE 
                WHEN total_attempts > 0 THEN 
                    (COALESCE(incorrect_count, 0) * 100.0 / total_attempts) * 2.0
                ELSE 0
            END) +
            ((6 - COALESCE(difficulty, 3)) * 10.0) +
            (CASE 
                WHEN last_asked < (? - 3600) THEN 50.0      
                WHEN last_asked < (? - 1800) THEN 30.0      
                WHEN last_asked < (? - 600) THEN 20.0       
                WHEN last_asked < (? - 300) THEN 10.0       
                ELSE 0
            END)
        DESC
        LIMIT 1
    """, (current_time, current_time, current_time, current_time, current_time, current_time, current_time))
    
    data = cursor.fetchone()
    conn.close()
    return data

# Test-Szenario
print("=" * 60)
print("TEST: Simuliere App-Nutzung")
print("=" * 60)

for i in range(3):
    print(f"\n--- Iteration {i+1} ---")
    
    # 1. Zeige aktuelle Vokabel
    vok = get_smart_vocabel_test()
    print(f"Aktuelle Vokabel: ID={vok[0]}, {vok[1]} <-> {vok[2]}")
    
    # 2. Benutzer antwortet (simuliert)
    is_correct = (i % 2 == 0)  # Abwechselnd richtig/falsch
    print(f"Benutzer antwortet: {'RICHTIG' if is_correct else 'FALSCH'}")
    
    # 3. Speichere Ergebnis
    update_vocabel_result_test(vok[0], is_correct)
    print(f"Ergebnis gespeichert")
    
    # 4. Lade nächste Vokabel
    next_vok = get_smart_vocabel_test()
    print(f"Nächste Vokabel: ID={next_vok[0]}, {next_vok[1]} <-> {next_vok[2]}")
    
    # Prüfe ob sich die Vokabel geändert hat
    if vok[0] == next_vok[0]:
        print("⚠️ WARNUNG: Gleiche Vokabel wurde wieder ausgewählt!")
    else:
        print("✓ OK: Andere Vokabel ausgewählt")

print("\n" + "=" * 60)
print("TEST ABGESCHLOSSEN")
print("=" * 60)
