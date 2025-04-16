import sqlite3
import pathlib

def setup_local_database(app):
    """Create an SQLite database for offline storage if it doesn't exist."""
    db_dir = pathlib.Path(app.paths.app)
    db_dir.mkdir(parents=True, exist_ok=True)

    db_path = db_dir / f"activity_logs_{app.user_id}.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_type TEXT,
            time_frame TEXT,
            note TEXT,
            timestamp TEXT,
            synced INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()

    # Ensure timestamp column exists (legacy check)
    cursor.execute("PRAGMA table_info(activity_logs)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'timestamp' not in columns:
        cursor.execute("ALTER TABLE activity_logs ADD COLUMN timestamp TEXT")
        conn.commit()

    print(f"✅ Local SQLite database initialized at: {db_path}")
    return conn, cursor


def insert_entry(cursor, conn, entry):
    """Insert a single entry into local SQLite database."""
    cursor.execute("""
        INSERT INTO activity_logs (goal_type, time_frame, note, timestamp, synced)
        VALUES (?, ?, ?, ?, ?)
    """, (entry["goal_type"], entry["time_frame"], entry["note"], entry["timestamp"], 0))
    conn.commit()
    print("✅ Data saved to SQLite:", entry)


def get_all_entries(cursor):
    cursor.execute("SELECT goal_type, time_frame, note, timestamp FROM activity_logs")
    rows = cursor.fetchall()
    return [{"goal_type": row[0], "time_frame": row[1], "note": row[2], "timestamp": row[3]} for row in rows]


def get_unsynced_entries(cursor):
    cursor.execute("SELECT id, goal_type, time_frame, note, timestamp FROM activity_logs WHERE synced = 0")
    return cursor.fetchall()


def mark_entry_as_synced(cursor, conn, entry_id):
    cursor.execute("UPDATE activity_logs SET synced = 1 WHERE id = ?", (entry_id,))
    conn.commit()


# ✅ NEW META TABLE HELPERS

def set_meta_value(conn, key, value):
    conn.execute('REPLACE INTO meta (key, value) VALUES (?, ?)', (key, value))
    conn.commit()

def get_meta_value(conn, key):
    cursor = conn.execute('SELECT value FROM meta WHERE key = ?', (key,))
    result = cursor.fetchone()
    return result[0] if result else None
