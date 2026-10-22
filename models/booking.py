class Booking:
    """Holds the details of one booking."""

    def __init__(self, booking_id, user_id, resource_id, campus_id,
                 booking_date, start_time, duration_min, status="active"):
        self.booking_id = booking_id
        self.user_id = user_id
        self.resource_id = resource_id
        self.campus_id = campus_id
        self.booking_date = booking_date
        self.start_time = start_time
        self.duration_min = duration_min
        self.status = status

    def __str__(self):
        return f"Booking {self.booking_id}: {self.booking_date} at {self.start_time} for {self.duration_min} min"