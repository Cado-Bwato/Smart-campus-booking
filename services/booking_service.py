from datetime import datetime, timedelta
from database.db_manager import get_connection
from rules.booking_rules import get_rule


def time_to_minutes(time_text):
    """Turn "09:30" into 570 so we can compare times with maths."""
    hours, minutes = time_text.split(":")
    return int(hours) * 60 + int(minutes)


def get_policy_key(campus_id):
    """Find the policy_key (like "jhb") of a campus."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT policy_key FROM campuses WHERE campus_id = ?", (campus_id,))
    row = cur.fetchone()
    conn.close()
    return row["policy_key"] if row else None

def has_overlap(resource_id, booking_date, new_start, new_end):
    """Return True if this resource is already booked during that time."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT start_time, duration_min FROM bookings "
        "WHERE resource_id = ? AND booking_date = ? AND status = 'active'",
        (resource_id, booking_date)
    )
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        existing_start = time_to_minutes(row["start_time"])
        existing_end = existing_start + row["duration_min"]
        if new_start < existing_end and new_end > existing_start:
            return True
    return False

def create_booking(user_id, resource_id, campus_id, booking_date, start_time, duration_min):
    """Try to create a booking. Returns (True/False, message)."""
    # 1. Check the date, time and duration are valid
    try:
        start_dt = datetime.strptime(f"{booking_date} {start_time}", "%Y-%m-%d %H:%M")
        duration_min = int(duration_min)
    except ValueError:
        return False, "Date must be YYYY-MM-DD and time must be HH:MM."

    if duration_min <= 0:
        return False, "Duration must be more than 0 minutes."

    start_time = start_dt.strftime("%H:%M")       # tidy "9:00" into "09:00"

    # 2. Not in the past
    if start_dt < datetime.now():
        return False, "You cannot book a time in the past."

    # 3. Resource must exist and belong to the selected campus
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT campus_id FROM resources WHERE resource_id = ?", (resource_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False, "Resource not found."
    if row["campus_id"] != campus_id:
        return False, "This resource does not belong to the selected campus."

    # 4. Apply the campus booking rules
    rule = get_rule(get_policy_key(campus_id))
    allowed, message = rule.check(start_time, duration_min)
    if not allowed:
        return False, message

    # 5. Prevent overlapping bookings
    start_min = time_to_minutes(start_time)
    if has_overlap(resource_id, booking_date, start_min, start_min + duration_min):
        return False, "This resource is already booked at that time."

    # 6. All checks passed, so save it
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bookings (user_id, resource_id, campus_id, booking_date, start_time, duration_min) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, resource_id, campus_id, booking_date, start_time, duration_min)
    )
    conn.commit()
    conn.close()
    return True, "Booking confirmed."

def get_booked_slots(resource_id, booking_date):
    """Return a list of (start, end) times that are already booked."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT start_time, duration_min FROM bookings "
        "WHERE resource_id = ? AND booking_date = ? AND status = 'active' "
        "ORDER BY start_time",
        (resource_id, booking_date)
    )
    rows = cur.fetchall()
    conn.close()

    slots = []
    for row in rows:
        start = time_to_minutes(row["start_time"])
        end = start + row["duration_min"]
        slots.append((row["start_time"], f"{end // 60:02d}:{end % 60:02d}"))
    return slots

def get_user_bookings(user_id):
    """Return (active_list, past_list) for one lecturer."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT b.*, r.resource_code, r.name AS resource_name, c.name AS campus_name "
        "FROM bookings b "
        "JOIN resources r ON b.resource_id = r.resource_id "
        "JOIN campuses c ON b.campus_id = c.campus_id "
        "WHERE b.user_id = ? ORDER BY b.booking_date, b.start_time",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()

    active = []
    past = []
    now = datetime.now()

    for row in rows:
        start_dt = datetime.strptime(f"{row['booking_date']} {row['start_time']}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=row["duration_min"])

        if row["status"] == "active" and end_dt >= now:
            active.append(row)
        else:
            past.append(row)

    return active, past

def cancel_booking(booking_id, user_id):
    """Cancel a future booking that belongs to this user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings WHERE booking_id = ? AND user_id = ?", (booking_id, user_id))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return False, "Booking not found."

    if row["status"] == "cancelled":
        conn.close()
        return False, "This booking is already cancelled."

    start_dt = datetime.strptime(f"{row['booking_date']} {row['start_time']}", "%Y-%m-%d %H:%M")
    if start_dt <= datetime.now():
        conn.close()
        return False, "Only future bookings can be cancelled."

    cur.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return True, "Booking cancelled."



