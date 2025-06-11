import sqlite3
from datetime import datetime

def log_tv_status(status, room):
    conn = sqlite3.connect("TvLogger.db")
    cursor = conn.cursor()

    # Tabloyu oda bilgisiyle oluştur
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TVLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO TVLog (room, status, timestamp) VALUES (?, ?, ?)", (room, status, timestamp))
    conn.commit()
    conn.close()
