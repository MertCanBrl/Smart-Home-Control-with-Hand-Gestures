import sqlite3
from datetime import datetime

def log_light_status(status, room):
    conn = sqlite3.connect("LightLogger.db")
    cursor = conn.cursor()

    # Tabloyu oda bilgisiyle oluştur
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LightLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO LightLog (room, status, timestamp) VALUES (?, ?, ?)", (room, status, timestamp))
    conn.commit()
    conn.close()
