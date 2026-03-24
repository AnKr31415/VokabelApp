import os
import time
import psycopg2
import pandas as pd

DB_DSN = os.getenv(
    'NEON_DSN',
    'postgresql://neondb_owner:npg_3ULwGa4pZosX@ep-gentle-rice-altl6xsy-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
)

def get_conn():
    return psycopg2.connect(DB_DSN)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS vokabeln (
                   id SERIAL PRIMARY KEY,
                   deutsch TEXT NOT NULL,
                   englisch TEXT NOT NULL,
                   difficulty INTEGER DEFAULT 3,
                   correct_count INTEGER DEFAULT 0,
                   incorrect_count INTEGER DEFAULT 0,
                   last_asked DOUBLE PRECISION DEFAULT 0,
                   next_review DOUBLE PRECISION DEFAULT 0,
                   total_attempts INTEGER DEFAULT 0
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS settings (
                   key TEXT PRIMARY KEY,
                   value TEXT NOT NULL
                   )
                   """)

    conn.commit()
    conn.close()

def add_vocabel(deutsch, englisch):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO vokabeln (deutsch, englisch) VALUES (%s, %s)",
        (deutsch, englisch)
    )

    conn.commit()
    conn.close()

def delete_vokabel(vok_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vokabeln WHERE id = %s", (vok_id,))
    conn.commit()
    conn.close()

def get_all_vocabeln():
    conn = get_conn()
    cursor = conn.cursor()

    # die id mitliefern, damit man später löschen kann
    cursor.execute("SELECT id, deutsch, englisch FROM vokabeln")
    data = cursor.fetchall()

    conn.close()
    return data

def get_random_vokabel():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT deutsch, englisch FROM vokabeln ORDER BY RANDOM() LIMIT 1"
    )
    data = cursor.fetchone()

    conn.close()
    return data

def get_vocabel_by_deutsch(deutsch):
    result = get_random_vokabel()
    return result[0] if result else None

def get_vocabel_by_englisch(englisch):
    result = get_random_vokabel()
    return result[1] if result else None

def search_vokabel_by_deutsch(deutsch):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT deutsch, englisch FROM vokabeln WHERE LOWER(deutsch) = %s",
        (deutsch.strip().lower(),)
    )
    result = cursor.fetchone()
    conn.close()
    return result 

def search_vocabel_by_englisch(englisch):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT deutsch, englisch FROM vokabeln WHERE englisch ILIKE %s",
        (f"%{englisch}%",)
    )
    data = cursor.fetchone()
    conn.close()
    return data


# ===== NEUE INTELLIGENTE FUNKTIONEN =====

def migrate_db():
    """Fügt neue Spalten zu bestehender Tabelle hinzu (wenn sie nicht existieren)"""
    conn = get_conn()
    cursor = conn.cursor()
    
    required_cols = {
        'difficulty': 'INTEGER DEFAULT 3',
        'correct_count': 'INTEGER DEFAULT 0',
        'incorrect_count': 'INTEGER DEFAULT 0',
        'last_asked': 'DOUBLE PRECISION DEFAULT 0',
        'next_review': 'DOUBLE PRECISION DEFAULT 0',
        'total_attempts': 'INTEGER DEFAULT 0'
    }

    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'vokabeln'")
    existing = {r[0] for r in cursor.fetchall()}

    for name, ddl in required_cols.items():
        if name not in existing:
            cursor.execute(f"ALTER TABLE vokabeln ADD COLUMN {name} {ddl}")

    conn.commit()
    conn.close()


def update_vocabel_result(vok_id, is_correct):
    """
    Aktualisiert Statistiken für eine Vokabel
    is_correct: True = richtig beantwortet, False = falsch
    """
    conn = get_conn()
    cursor = conn.cursor()
    
    current_time = time.time()
    
    if is_correct:
        cursor.execute("""
            UPDATE vokabeln 
            SET correct_count = correct_count + 1,
                total_attempts = total_attempts + 1,
                last_asked = %s,
                next_review = %s
            WHERE id = %s
        """, (current_time, current_time + 86400, vok_id))  # nächste Wiederholung in 24h
    else:
        cursor.execute("""
            UPDATE vokabeln 
            SET incorrect_count = incorrect_count + 1,
                total_attempts = total_attempts + 1,
                last_asked = %s,
                next_review = %s
            WHERE id = %s
        """, (current_time, current_time + 300, vok_id))  # nächste Wiederholung in 5min
    
    conn.commit()
    conn.close()


def set_vocabel_difficulty(vok_id, difficulty):
    """
    Setzt Schwierigkeitsbewertung (1-5)
    1 = kann kaum = wird am häufigsten gefragt
    5 = kann sehr gut = wird selten gefragt
    """
    conn = get_conn()
    cursor = conn.cursor()
    
    difficulty = max(1, min(5, difficulty))  # zwischen 1-5
    cursor.execute(
        "UPDATE vokabeln SET difficulty = %s WHERE id = %s",
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
    conn = get_conn()
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
                WHEN last_asked > (%s - 20) THEN -999.0      -- Gerade (<20s) gefragt
                WHEN last_asked > (%s - 120) THEN -100.0     -- Gerade (<2min) gefragt
                WHEN last_asked > (%s - 300) THEN -50.0      -- Gerade (<5min) gefragt
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
                WHEN last_asked < (%s - 3600) THEN 50.0      -- >1h nicht gefragt
                WHEN last_asked < (%s - 1800) THEN 30.0      -- >30min nicht gefragt
                WHEN last_asked < (%s - 600) THEN 20.0       -- >10min nicht gefragt
                WHEN last_asked < (%s - 300) THEN 10.0       -- >5min nicht gefragt
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
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, deutsch, englisch, difficulty, correct_count, incorrect_count FROM vokabeln WHERE id = %s",
        (vok_id,)
    )
    data = cursor.fetchone()
    conn.close()
    return data


def get_vocabel_stats(vok_id):
    """Holt Statistiken für eine Vokabel"""
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT correct_count, incorrect_count, difficulty, total_attempts FROM vokabeln WHERE id = %s",
        (vok_id,)
    )
    data = cursor.fetchone()
    conn.close()
    return data if data else (0, 0, 3, 0)


def import_from_excel(file_path):
    """
    Importiert Vokabeln aus einer Excel-Datei.
    Erwartet Spalten: 'deutsch' und 'englisch'
    """
    try:
        # Excel-Datei lesen
        df = pd.read_excel(file_path)
        
        # Überprüfen, ob die erforderlichen Spalten vorhanden sind
        if 'deutsch' not in df.columns or ('englisch' and 'französisch') not in df.columns:
            raise ValueError("Die Excel-Datei muss Spalten 'deutsch' und 'englisch' enthalten.")
        
        conn = get_conn()
        cursor = conn.cursor()
        
        imported_count = 0
        for _, row in df.iterrows():
            deutsch = str(row['deutsch']).strip()
            englisch = str(row['englisch']).strip() if 'englisch' in df.columns else str(row['französisch']).strip()
            
            if deutsch and englisch:  # Nur einfügen, wenn beide Werte vorhanden
                cursor.execute(
                    "INSERT INTO vokabeln (deutsch, englisch) VALUES (%s, %s)",
                    (deutsch, englisch)
                )
                imported_count += 1
        
        conn.commit()
        conn.close()
        
        return f"Erfolgreich {imported_count} Vokabeln importiert."
    
    except Exception as e:
        return f"Fehler beim Import: {str(e)}"


# ===== SETTINGS FUNCTIONS =====

def get_setting(key, default=None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = %s", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default

def set_setting(key, value):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (key, value) VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (key, value))
    conn.commit()
    conn.close()