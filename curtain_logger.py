import sqlite3
from datetime import datetime

def log_curtain_status(status, room):
    conn = sqlite3.connect("CurtainLogger.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CurtainLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO CurtainLog (room, status, timestamp) VALUES (?, ?, ?)", (room, status, timestamp))
    conn.commit()
    conn.close()
