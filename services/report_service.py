from database.db_manager import get_connection


def get_campus_report(campus_id):
    """Return a dictionary of report numbers for one campus."""
    conn = get_connection()
    cur = conn.cursor()

    # Total and average (cancelled bookings are not counted)
    cur.execute(
        "SELECT COUNT(*) AS total, AVG(duration_min) AS average "
        "FROM bookings WHERE campus_id = ? AND status = 'active'",
        (campus_id,)
    )
    row = cur.fetchone()
    total = row["total"]
    average = round(row["average"], 1) if row["average"] is not None else 0

    # Cancelled bookings
    cur.execute(
        "SELECT COUNT(*) FROM bookings WHERE campus_id = ? AND status = 'cancelled'",
        (campus_id,)
    )
    cancelled = cur.fetchone()[0]

    # Most frequently used resources (top 5)
    cur.execute(
        "SELECT r.resource_code, r.name, COUNT(*) AS uses, SUM(b.duration_min) AS minutes "
        "FROM bookings b JOIN resources r ON b.resource_id = r.resource_id "
        "WHERE b.campus_id = ? AND b.status = 'active' "
        "GROUP BY r.resource_id ORDER BY uses DESC LIMIT 5",
        (campus_id,)
    )
    top_resources = cur.fetchall()
    conn.close()

    return {
        "total_bookings": total,
        "cancelled_bookings": cancelled,
        "average_duration": average,
        "top_resources": top_resources,
    }
def get_usage_trend(campus_id):
    """Return a list of (date, number_of_bookings) for one campus."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT booking_date, COUNT(*) AS total "
        "FROM bookings WHERE campus_id = ? AND status = 'active' "
        "GROUP BY booking_date ORDER BY booking_date",
        (campus_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_usage_trend(campus_id):
    """Return a list of (date, number_of_bookings) for one campus."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT booking_date, COUNT(*) AS total "
        "FROM bookings WHERE campus_id = ? AND status = 'active' "
        "GROUP BY booking_date ORDER BY booking_date",
        (campus_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_campus_bookings(campus_id):
    """Return every booking for one campus, with names instead of numbers."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT b.booking_id, b.booking_date, b.start_time, b.duration_min, b.status, "
        "r.resource_code, u.full_name "
        "FROM bookings b "
        "JOIN resources r ON b.resource_id = r.resource_id "
        "JOIN users u ON b.user_id = u.user_id "
        "WHERE b.campus_id = ? ORDER BY b.booking_date, b.start_time",
        (campus_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

from rules.booking_rules import get_rule


def get_comparison_report():
    """Return a list of dictionaries, one per campus, for comparison."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT campus_id, name, policy_key FROM campuses ORDER BY name")
    campuses = cur.fetchall()
    conn.close()

    results = []
    for campus in campuses:
        report = get_campus_report(campus["campus_id"])
        rule = get_rule(campus["policy_key"])

        if report["top_resources"]:
            busiest = report["top_resources"][0]["resource_code"]
        else:
            busiest = "None"

        results.append({
            "campus": campus["name"],
            "total_bookings": report["total_bookings"],
            "cancelled": report["cancelled_bookings"],
            "average_duration": report["average_duration"],
            "busiest_resource": busiest,
            "max_minutes_rule": rule.max_minutes,
            "opening_hours": f"{rule.open_time} - {rule.close_time}",
        })
    return results

def get_all_bookings(campus_id=None):
    """Return bookings across campuses. If campus_id is given, only that campus."""
    conn = get_connection()
    cur = conn.cursor()

    sql = ("SELECT b.booking_id, b.booking_date, b.start_time, b.duration_min, b.status, "
           "c.name AS campus_name, r.resource_code, u.full_name "
           "FROM bookings b "
           "JOIN campuses c ON b.campus_id = c.campus_id "
           "JOIN resources r ON b.resource_id = r.resource_id "
           "JOIN users u ON b.user_id = u.user_id ")

    if campus_id is None:
        cur.execute(sql + "ORDER BY b.booking_date, b.start_time")
    else:
        cur.execute(sql + "WHERE b.campus_id = ? ORDER BY b.booking_date, b.start_time",
                    (campus_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_resource_usage_all():
    """Return usage of every resource, grouped by campus (includes unused resources)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT c.name AS campus_name, r.resource_code, r.name, "
        "COUNT(b.booking_id) AS uses, COALESCE(SUM(b.duration_min), 0) AS minutes "
        "FROM resources r "
        "JOIN campuses c ON r.campus_id = c.campus_id "
        "LEFT JOIN bookings b ON b.resource_id = r.resource_id AND b.status = 'active' "
        "GROUP BY r.resource_id "
        "ORDER BY c.name, uses DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return rows