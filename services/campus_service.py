from database.db_manager import get_connection
from models.campus import Campus


def make_campus(row):
    """Turn a database row into a Campus object."""
    return Campus(row["campus_id"], row["name"], row["policy_key"])


def get_all_campuses():
    """Return a list of Campus objects."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM campuses ORDER BY name")
    rows = cur.fetchall()
    conn.close()

    campuses = []
    for row in rows:
        campuses.append(make_campus(row))
    return campuses


def get_campus(campus_id):
    """Return one Campus object, or None if it does not exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM campuses WHERE campus_id = ?", (campus_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None
    return make_campus(row)