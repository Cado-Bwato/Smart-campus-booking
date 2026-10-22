# auth_service.py - registration, login and starter accounts
import sqlite3
from database.db_manager import get_connection
from models.user import Lecturer, CampusAdmin, SystemOperator
from models.security import hash_password


def make_user(row):
    """Turn a database row into a Lecturer, CampusAdmin or SystemOperator."""
    if row["role"] == "lecturer":
        return Lecturer(row["user_id"], row["username"], row["password"],
                        row["full_name"], row["campus_id"])
    elif row["role"] == "admin":
        return CampusAdmin(row["user_id"], row["username"], row["password"],
                           row["full_name"], row["campus_id"])
    else:
        return SystemOperator(row["user_id"], row["username"], row["password"],
                              row["full_name"])


def register_lecturer(username, password, full_name):
    """Create a new lecturer account. Returns (True/False, message)."""
    username = username.strip()
    full_name = full_name.strip()

    if username == "" or password == "" or full_name == "":
        return False, "Please fill in all fields."

    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), full_name, "lecturer")
        )
        conn.commit()
        return True, "Account created. You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    finally:
        conn.close()


def login(username, password):
    """Check username and password. Returns (user object or None, message)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None, "Username not found."

    user = make_user(row)

    if not user.check_password(password):
        return None, "Incorrect password."

    return user, "Login successful."


def seed_default_users():
    """Create starter admin and operator accounts, only if no users exist yet."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (username, password, full_name, role, campus_id) VALUES (?, ?, ?, ?, ?)",
                    ("admin_jhb", hash_password("admin123"), "Johannesburg Admin", "admin", 1))
        cur.execute("INSERT INTO users (username, password, full_name, role, campus_id) VALUES (?, ?, ?, ?, ?)",
                    ("admin_dbn", hash_password("admin123"), "Durban Admin", "admin", 2))
        cur.execute("INSERT INTO users (username, password, full_name, role, campus_id) VALUES (?, ?, ?, ?, ?)",
                    ("admin_cpt", hash_password("admin123"), "Cape Town Admin", "admin", 3))
        cur.execute("INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                    ("operator", hash_password("op123"), "System Operator", "operator"))
        conn.commit()

    conn.close()