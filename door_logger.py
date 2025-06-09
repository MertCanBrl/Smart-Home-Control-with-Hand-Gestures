import sqlite3
from datetime import datetime

def log_door_status(status, room):
    conn = sqlite3.connect("DoorLogger.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DoorLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO DoorLog (room, status, timestamp) VALUES (?, ?, ?)", (room, status, timestamp))
    conn.commit()
    conn.close()
