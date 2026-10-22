# booking_rules.py - the booking policy of each campus (kept separate from the main logic)
class BookingRule:
    """Parent class. Holds the rules every campus must follow."""

    def __init__(self, campus_name, max_minutes, open_time, close_time):
        self.campus_name = campus_name
        self.max_minutes = max_minutes      # longest booking allowed
        self.open_time = open_time          # earliest start, e.g. "08:00"
        self.close_time = close_time        # booking must finish by this time

    def time_to_minutes(self, time_text):
        """Turn "09:30" into 570 so we can compare times with maths."""
        hours, minutes = time_text.split(":")
        return int(hours) * 60 + int(minutes)

    def check(self, start_time, duration_min):
        """Return (True, message) if allowed, or (False, reason) if not."""
        if duration_min > self.max_minutes:
            return False, f"Maximum booking length at {self.campus_name} is {self.max_minutes} minutes."

        start = self.time_to_minutes(start_time)
        end = start + duration_min

        if start < self.time_to_minutes(self.open_time) or end > self.time_to_minutes(self.close_time):
            return False, (f"Bookings at {self.campus_name} are only allowed "
                           f"between {self.open_time} and {self.close_time}.")

        return True, "Booking allowed"

    def describe(self):
        """Text we will show in the GUI so users see which policy applies."""
        return (f"{self.campus_name} policy: max {self.max_minutes} minutes per booking, "
                f"open {self.open_time} to {self.close_time}")

class JohannesburgRule(BookingRule):
    def __init__(self):
        super().__init__("Johannesburg", 120, "08:00", "17:00")


class DurbanRule(BookingRule):
    def __init__(self):
        super().__init__("Durban", 90, "07:00", "16:00")


class CapeTownRule(BookingRule):
    def __init__(self):
        super().__init__("Cape Town", 180, "09:00", "18:00")

# Dictionary: policy_key from the database -> rule object
RULES = {
    "jhb": JohannesburgRule(),
    "dbn": DurbanRule(),
    "cpt": CapeTownRule(),
}


def get_rule(policy_key):
    """Find the rule object for a campus using its policy_key."""
    return RULES[policy_key]