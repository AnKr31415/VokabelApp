import sqlite3

DB_NAME = "vokabeln.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS vokabeln (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   deutsch TEXT NOT NULL,
                   englisch TEXT NOT NULL
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