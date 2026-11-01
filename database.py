import sqlite3

DB_NAME = "parking.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parking_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            slot_number INTEGER NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            amount REAL DEFAULT 0,
            status TEXT DEFAULT 'Parked'
        )
    """)
    conn.commit()
    conn.close()