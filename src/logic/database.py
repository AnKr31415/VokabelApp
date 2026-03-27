import os
import time
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DB_DSN = os.getenv('NEON_DSN')

def get_connection():
    return psycopg2.connect(DB_DSN)

# ===== INIT =====
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabellen für relationales Design
    cursor.execute("CREATE TABLE IF NOT EXISTS concepts (id SERIAL PRIMARY KEY, created_at DOUBLE PRECISION DEFAULT EXTRACT(EPOCH FROM NOW()))")
    cursor.execute("CREATE TABLE IF NOT EXISTS languages (id SERIAL PRIMARY KEY, code VARCHAR(10) UNIQUE NOT NULL, name TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS translations (id SERIAL PRIMARY KEY, concept_id INTEGER REFERENCES concepts(id) ON DELETE CASCADE, language_id INTEGER REFERENCES languages(id) ON DELETE CASCADE, word TEXT NOT NULL, UNIQUE(concept_id, language_id))")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id SERIAL PRIMARY KEY, 
            concept_id INTEGER REFERENCES concepts(id) ON DELETE CASCADE, 
            source_lang_id INTEGER REFERENCES languages(id), 
            target_lang_id INTEGER REFERENCES languages(id), 
            difficulty INTEGER DEFAULT 3, 
            correct_count INTEGER DEFAULT 0, 
            incorrect_count INTEGER DEFAULT 0, 
            last_asked DOUBLE PRECISION DEFAULT 0, 
            next_review DOUBLE PRECISION DEFAULT 0, 
            UNIQUE(concept_id, source_lang_id, target_lang_id)
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")

    # Standardsprachen
    langs = [('de', 'Deutsch'), ('en', 'Englisch'), ('fr', 'Französisch'), ('es', 'Spanisch')]
    for code, name in langs:
        cursor.execute("INSERT INTO languages (code, name) VALUES (%s, %s) ON CONFLICT (code) DO NOTHING", (code, name))
    
    conn.commit()
    conn.close()

# ===== HILFSFUNKTIONEN =====
def get_lang_id(name_or_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM languages WHERE name = %s OR code = %s", (name_or_code, name_or_code))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

# ===== SETTINGS =====
def get_setting(key, default=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = %s", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default
    except: return default

def set_setting(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value", (key, str(value)))
    conn.commit()
    conn.close()

# ===== CRUD =====
def get_all_vocabeln():
    """Gibt alle Vokabeln in einem flachen Format zurück, das dein GUI versteht."""
    conn = get_connection()
    # DictCursor ist wichtig, damit vok['de'] funktioniert
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Dieser Query baut die relationale Struktur für das GUI wieder "flach" zusammen
    query = """
    SELECT c.id, 
           MAX(CASE WHEN l.name = 'Deutsch' THEN t.word END) as de,
           MAX(CASE WHEN l.name = 'Englisch' THEN t.word END) as en,
           MAX(CASE WHEN l.name = 'Französisch' THEN t.word END) as fr,
           MAX(CASE WHEN l.name = 'Spanisch' THEN t.word END) as es
    FROM concepts c
    LEFT JOIN translations t ON c.id = t.concept_id
    LEFT JOIN languages l ON t.language_id = l.id
    GROUP BY c.id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

def get_smart_vocabel(source, target):
    """
    Sucht eine Vokabel und benennt die Spalten so um, 
    dass vok['Deutsch'] oder vok['Englisch'] funktioniert.
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    s_id = get_lang_id(source)
    t_id = get_lang_id(target)
    
    # Wir nutzen 'AS' im SQL, um die Spaltennamen 
    # exakt an self.source_lang anzupassen
    query = f"""
        SELECT 
            c.id, 
            t1.word AS "{source}", 
            t2.word AS "{target}"
        FROM concepts c
        JOIN translations t1 ON c.id = t1.concept_id AND t1.language_id = %s
        JOIN translations t2 ON c.id = t2.concept_id AND t2.language_id = %s
        ORDER BY RANDOM() 
        LIMIT 1
    """
    
    try:
        cursor.execute(query, (s_id, t_id))
        res = cursor.fetchone()
        return res
    except Exception as e:
        print(f"Fehler bei get_smart_vocabel: {e}")
        return None
    finally:
        conn.close()


def add_vocabel(de, en, fr=None, es=None):
    """Klassische Signatur für den Excel-Import / GUI-Add."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO concepts DEFAULT VALUES RETURNING id")
    c_id = cursor.fetchone()[0]
    
    words = [('Deutsch', de), ('Englisch', en), ('Französisch', fr), ('Spanisch', es)]
    for lang_name, word in words:
        if word:
            l_id = get_lang_id(lang_name)
            cursor.execute("INSERT INTO translations (concept_id, language_id, word) VALUES (%s, %s, %s)", (c_id, l_id, word))
    conn.commit()
    conn.close()

def delete_vocabel(vok_id):
    """Löscht ein Konzept und gibt Feedback in die Konsole."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Wir führen das DELETE aus
        cursor.execute("DELETE FROM concepts WHERE id = %s", (vok_id,))
        
        # rowcount verrät uns, ob wirklich eine Zeile gelöscht wurde
        deleted_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted_rows > 0:
            print(f"✅ Datenbank: Konzept {vok_id} wurde wirklich gelöscht.")
        else:
            print(f"⚠️ Datenbank: Löschen fehlgeschlagen! ID {vok_id} existiert nicht.")
            
    except Exception as e:
        print(f"❌ Datenbank-Fehler beim Löschen: {e}")