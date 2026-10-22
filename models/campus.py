class Campus:
    """Holds the details of one campus."""

    def __init__(self, campus_id, name, policy_key):
        self.campus_id = campus_id
        self.name = name
        self.policy_key = policy_key

    def __str__(self):
        return self.name