import psycopg2
import os

DB_DSN = os.getenv(
    'NEON_DSN',
    'postgresql://neondb_owner:npg_3ULwGa4pZosX@ep-gentle-rice-altl6xsy-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
)

def get_conn():
    return psycopg2.connect(DB_DSN)

def migrate():
    conn = get_conn()
    cur = conn.cursor()

    # Tabelle erstellen, falls sie nicht existiert
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vocabeln (
        id SERIAL PRIMARY KEY
    )
    """)
    print("Tabelle 'vocabeln' existiert oder wurde erstellt.")

    # Spaltenliste mit Typen
    columns = {
        "de": "TEXT",
        "en": "TEXT",
        "fr": "TEXT",
        "es": "TEXT",
        "difficulty": "INTEGER DEFAULT 3",
        "correct_count": "INTEGER DEFAULT 0",
        "incorrect_count": "INTEGER DEFAULT 0",
        "last_asked": "TIMESTAMP",
        "next_review": "TIMESTAMP",
        "total_attempts": "INTEGER DEFAULT 0"
    }

    # Prüfen und Spalten hinzufügen
    for col_name, col_type in columns.items():
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='vocabeln' AND column_name=%s
        """, (col_name,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"ALTER TABLE vocabeln ADD COLUMN {col_name} {col_type}")
            print(f"Spalte '{col_name}' hinzugefügt.")

    conn.commit()
    cur.close()
    conn.close()
    print("Migration abgeschlossen. Alle Spalten vorhanden.")

if __name__ == "__main__":
    migrate()