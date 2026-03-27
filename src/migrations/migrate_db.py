import psycopg2
import os

# Datenbank-Verbindungsstring
DB_DSN = os.getenv(
    'NEON_DSN',
     'postgresql://neondb_owner:npg_3ULwGa4pZosX@ep-gentle-rice-altl6xsy-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
)

def get_conn():
    """Stellt eine Verbindung zur Datenbank her."""
    return psycopg2.connect(DB_DSN)

def migrate():
    """Prüft die Datenbankstruktur und erstellt die Tabelle 'vocabeln', falls sie fehlt."""
    conn = get_conn()
    cursor = conn.cursor()

    # Tabelle erstellen, falls sie nicht existiert
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocabeln (
        id SERIAL PRIMARY KEY,
        de TEXT,
        en TEXT,
        fr TEXT,
        es TEXT,
        difficulty INTEGER DEFAULT 3
    )
    """)
    print("Tabelle 'vocabeln' erstellt oder existiert bereits!")

    conn.commit()
    cursor.close()
    conn.close()
    print("Datenbankprüfung abgeschlossen.")

if __name__ == "__main__":
    migrate()