import sqlite3
from datetime import datetime, timedelta
import time

DB_NAME = "vokabeln.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS vokabeln (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   deutsch TEXT NOT NULL,
                   englisch TEXT NOT NULL,
                   difficulty INTEGER DEFAULT 3,
                   correct_count INTEGER DEFAULT 0,
                   incorrect_count INTEGER DEFAULT 0,
                   last_asked REAL DEFAULT 0,
                   next_review REAL DEFAULT 0,
                   total_attempts INTEGER DEFAULT 0
                   )
                   """)

    conn.commit()
    conn.close()

def add_vocabel(deutsch, englisch):
    conn= sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO vokabeln (deutsch, englisch) VALUES (?,?)",
        (deutsch, englisch)
    )

    conn.commit()
    conn.close()

def delete_vokabel(vok_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vokabeln WHERE id = ?", (vok_id,))
    conn.commit()
    conn.close()

def get_all_vocabeln():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # die id mitliefern, damit man später löschen kann
    cursor.execute("SELECT id, deutsch, englisch FROM vokabeln")
    data = cursor.fetchall()

    conn.close()
    return data

def get_random_vokabel():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT deutsch, englisch FROM vokabeln ORDER BY RANDOM() LIMIT 1"
    )
    data = cursor.fetchone()

    conn.close()
    return data

def get_vocabel_by_deutsch(deutsch):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    result = get_random_vokabel()
    deutsch = result[0]

    return deutsch

def get_vocabel_by_englisch(englisch):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    result = get_random_vokabel()
    englisch = result[1]

    return englisch

def search_vokabel_by_deutsch(deutsch):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT deutsch, englisch FROM vokabeln WHERE LOWER(deutsch) = ?",
        (deutsch.strip().lower(),)
    )
    result = cursor.fetchone()
    conn.close()
    return result 

def search_vocabel_by_englisch(englisch):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT deutsch, englisch FROM vokabeln WHERE englisch LIKE ?",
        (f"%{englisch}%",)
    )
    data = cursor.fetchone()
    conn.close()
    return data


# ===== NEUE INTELLIGENTE FUNKTIONEN =====

def migrate_db():
    """Fügt neue Spalten zu bestehender Tabelle hinzu (wenn sie nicht existieren)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Spalten hinzufügen, falls sie nicht existieren
    columns_to_add = [
        ("difficulty", "INTEGER DEFAULT 3"),
        ("correct_count", "INTEGER DEFAULT 0"),
        ("incorrect_count", "INTEGER DEFAULT 0"),
        ("last_asked", "REAL DEFAULT 0"),
        ("next_review", "REAL DEFAULT 0"),
        ("total_attempts", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_def in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE vokabeln ADD COLUMN {col_name} {col_def}")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits
    
    conn.commit()
    conn.close()


def update_vocabel_result(vok_id, is_correct):
    """
    Aktualisiert Statistiken für eine Vokabel
    is_correct: True = richtig beantwortet, False = falsch
    """
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
        """, (current_time, current_time + 86400, vok_id))  # nächste Wiederholung in 24h
    else:
        cursor.execute("""
            UPDATE vokabeln 
            SET incorrect_count = incorrect_count + 1,
                total_attempts = total_attempts + 1,
                last_asked = ?,
                next_review = ?
            WHERE id = ?
        """, (current_time, current_time + 300, vok_id))  # nächste Wiederholung in 5min
    
    conn.commit()
    conn.close()


def set_vocabel_difficulty(vok_id, difficulty):
    """
    Setzt Schwierigkeitsbewertung (1-5)
    1 = kann kaum = wird am häufigsten gefragt
    5 = kann sehr gut = wird selten gefragt
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    difficulty = max(1, min(5, difficulty))  # zwischen 1-5
    cursor.execute(
        "UPDATE vokabeln SET difficulty = ? WHERE id = ?",
        (difficulty, vok_id)
    )
    conn.commit()
    conn.close()


def get_smart_vocabel():
    """
    Intelligente Auswahl mit Rotation und Spaced Repetition:
    - Gerade gefragte Vokabeln = SEHR niedrige Priorität (Rotation)
    - Neue Vokabeln = höhe Priorität
    - Vokabeln mit niedriger Erfolgsquote = höhe Priorität
    - Schwierigkeit 1 = höhe Priorität
    - Lange nicht gefragt = höhe Priorität
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    current_time = time.time()
    
    # Strategie: Es muss immer VERSCHIEDENE Vokabeln geben
    # 1. Zuerst neue Vokabeln (last_asked = 0)
    # 2. Dann Vokabeln mit niedrigem Erfolgs-Prozentsatz
    # 3. Dann Schwierigkeits-Faktor
    # 4. ABER - NICHT das, was gerade gefragt wurde!
    
    cursor.execute("""
        SELECT id, deutsch, englisch FROM vokabeln
        WHERE vokabeln.id > 0
        ORDER BY 
            -- WICHTIG: Gerade gefragte Vokabeln: EXTREM niedrig
            (CASE 
                WHEN last_asked > (? - 20) THEN -999.0      -- Gerade (<20s) gefragt
                WHEN last_asked > (? - 120) THEN -100.0     -- Gerade (<2min) gefragt
                WHEN last_asked > (? - 300) THEN -50.0      -- Gerade (<5min) gefragt
                ELSE 0
            END) +
            -- Priorität 1: Neue Vokabeln (never asked)
            (CASE 
                WHEN last_asked = 0 OR total_attempts = 0 THEN 100.0
                ELSE 0
            END) +
            -- Priorität 2: Erfolgsquote (je niedriger, desto höher)
            (CASE 
                WHEN total_attempts > 0 THEN 
                    (COALESCE(incorrect_count, 0) * 100.0 / total_attempts) * 2.0
                ELSE 0
            END) +
            -- Priorität 3: Schwierigkeit (1=max)
            ((6 - COALESCE(difficulty, 3)) * 10.0) +
            -- Priorität 4: Lange nicht gefragt
            (CASE 
                WHEN last_asked < (? - 3600) THEN 50.0      -- >1h nicht gefragt
                WHEN last_asked < (? - 1800) THEN 30.0      -- >30min nicht gefragt
                WHEN last_asked < (? - 600) THEN 20.0       -- >10min nicht gefragt
                WHEN last_asked < (? - 300) THEN 10.0       -- >5min nicht gefragt
                ELSE 0
            END)
        DESC
        LIMIT 1
    """, (current_time, current_time, current_time, current_time, current_time, current_time, current_time))
    
    data = cursor.fetchone()
    conn.close()
    return data


def get_vocabel_with_id(vok_id):
    """Holt Vokabel mit ID zurück (mit allen Stats)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, deutsch, englisch, difficulty, correct_count, incorrect_count FROM vokabeln WHERE id = ?",
        (vok_id,)
    )
    data = cursor.fetchone()
    conn.close()
    return data


def get_vocabel_stats(vok_id):
    """Holt Statistiken für eine Vokabel"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT correct_count, incorrect_count, difficulty, total_attempts FROM vokabeln WHERE id = ?",
        (vok_id,)
    )
    data = cursor.fetchone()
    conn.close()
    return data if data else (0, 0, 3, 0)