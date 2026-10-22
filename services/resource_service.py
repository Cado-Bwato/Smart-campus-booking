import sqlite3
from database.db_manager import get_connection
from models.resource import Resource


def make_resource(row):
    """Turn a database row into a Resource object."""
    return Resource(row["resource_id"], row["resource_code"], row["name"],
                    row["resource_type"], row["campus_id"])

def add_resource(resource_code, name, resource_type, campus_id):
    """Add a resource to a campus. Returns (True/False, message)."""
    resource_code = resource_code.strip().upper()
    name = name.strip()
    resource_type = resource_type.strip()

    if resource_code == "" or name == "" or resource_type == "":
        return False, "Please fill in all fields."

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO resources (resource_code, name, resource_type, campus_id) VALUES (?, ?, ?, ?)",
            (resource_code, name, resource_type, campus_id)
        )
        conn.commit()
        return True, f"Resource {resource_code} added."
    except sqlite3.IntegrityError:
        return False, f"Resource code {resource_code} already exists."
    finally:
        conn.close()

def get_resources_by_campus(campus_id):
    """Return a list of Resource objects for one campus."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resources WHERE campus_id = ? ORDER BY resource_code", (campus_id,))
    rows = cur.fetchall()
    conn.close()

    resources = []
    for row in rows:
        resources.append(make_resource(row))
    return resources

def update_resource(resource_id, name, resource_type):
    """Change the name and type of a resource."""
    name = name.strip()
    resource_type = resource_type.strip()

    if name == "" or resource_type == "":
        return False, "Name and type cannot be empty."

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE resources SET name = ?, resource_type = ? WHERE resource_id = ?",
                (name, resource_type, resource_id))
    conn.commit()
    conn.close()
    return True, "Resource updated."

def remove_resource(resource_id):
    """Delete a resource, unless it still has active bookings."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM bookings WHERE resource_id = ? AND status = 'active'",
                (resource_id,))
    cur.execute("SELECT COUNT(*) FROM bookings WHERE resource_id = ?", (resource_id,))
    if cur.fetchone()[0] > 0:
        conn.close()
        return False, "Cannot remove: this resource has booking records that must be kept."

    cur.execute("DELETE FROM resources WHERE resource_id = ?", (resource_id,))
    conn.commit()
    conn.close()
    return True, "Resource removed."

def seed_resources():
    """Add a few sample resources, only if the table is empty."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM resources")
    count = cur.fetchone()[0]
    conn.close()

    if count == 0:
        add_resource("JHB-LAB-01", "Computer Lab 1", "Computer Lab", 1)
        add_resource("JHB-PRJ-01", "Projector A", "Projector", 1)
        add_resource("JHB-SEM-01", "Seminar Room 1", "Seminar Room", 1)
        add_resource("DBN-LAB-01", "Computer Lab 1", "Computer Lab", 2)
        add_resource("DBN-PRJ-01", "Projector A", "Projector", 2)
        add_resource("CPT-LAB-01", "Computer Lab 1", "Computer Lab", 3)
        add_resource("CPT-SEM-01", "Seminar Room 1", "Seminar Room", 3)