#!/usr/bin/env python3
"""Debug: Überprüfe neue Prioritäts-Berechnung"""
import sqlite3
import time

DB_NAME = "vokabeln.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

current_time = time.time()

# Vereinfachte Debug-Version der neuen Formel
cursor.execute("""
    SELECT 
        id, deutsch,
        COALESCE(difficulty, 3) as diff,
        COALESCE(incorrect_count, 0) as incorrect,
        COALESCE(total_attempts, 0) as total,
        COALESCE(correct_count, 0) as correct,
        PRINTF('%.0f%%', 
            CASE 
                WHEN total_attempts = 0 THEN 0
                ELSE COALESCE(incorrect_count, 0) * 100.0 / total_attempts
            END)
    FROM vokabeln
    ORDER BY 
        (CASE 
            WHEN last_asked > (? - 30) THEN -20.0        
            WHEN last_asked > (? - 120) THEN -10.0        
            ELSE 0
        END) +
        (CASE 
            WHEN total_attempts = 0 THEN 5.0              
            WHEN total_attempts > 0 THEN 
                (COALESCE(incorrect_count, 0) * 100.0 / total_attempts) * 0.5   
            ELSE 0
        END) +
        ((6 - COALESCE(difficulty, 3)) * 1.5) +
        (CASE 
            WHEN last_asked = 0 THEN 3.0                  
            WHEN last_asked < (? - 1800) THEN 3.0         
            WHEN last_asked < (? - 600) THEN 1.5          
            ELSE 0
        END)
    DESC
""", (current_time, current_time, current_time, current_time))

results = cursor.fetchall()
print("\nALLE VOKABELN - NEUE PRIORITÄTS-BERECHNUNG:")
print("=" * 100)
print(f"{'ID':<3} | {'Vokabel':<15} | {'Diff':<4} | {'Fehler':<8} | {'Versuche':<8} | {'Fehler %':<8}")
print("-" * 100)
for row in results:
    print(f"{row[0]:<3} | {row[1]:<15} | {row[2]:<4} | {row[3]:<8} | {row[4]:<8} | {row[6]:<8}")

print("\n" + "=" * 100)
print(f"✓ Vokabel mit höchster Priorität: {results[0][1]}\n")

conn.close()
