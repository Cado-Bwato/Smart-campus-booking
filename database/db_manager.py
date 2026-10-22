import os
import sqlite3

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_FOLDER, "smart_campus_final.db")


def get_connection():
    """Open a connection to the database file."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create all the tables if they do not exist yet."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS campuses (
            campus_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            policy_key  TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL,
            full_name   TEXT NOT NULL,
            role        TEXT NOT NULL,
            campus_id   INTEGER,
            FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            resource_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_code  TEXT NOT NULL UNIQUE,
            name           TEXT NOT NULL,
            resource_type  TEXT NOT NULL,
            campus_id      INTEGER NOT NULL,
            FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            resource_id   INTEGER NOT NULL,
            campus_id     INTEGER NOT NULL,
            booking_date  TEXT NOT NULL,
            start_time    TEXT NOT NULL,
            duration_min  INTEGER NOT NULL,
            status        TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (user_id)     REFERENCES users(user_id),
            FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
            FOREIGN KEY (campus_id)   REFERENCES campuses(campus_id)
        )
    """)
    conn.commit()
    conn.close()

def seed_campuses():
    """Add 3 starting campuses, but only if the table is empty."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM campuses")
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute("INSERT INTO campuses (name, policy_key) VALUES (?, ?)", ("Johannesburg", "jhb"))
        cur.execute("INSERT INTO campuses (name, policy_key) VALUES (?, ?)", ("Durban", "dbn"))
        cur.execute("INSERT INTO campuses (name, policy_key) VALUES (?, ?)", ("Cape Town", "cpt"))
        conn.commit()

    conn.close()



