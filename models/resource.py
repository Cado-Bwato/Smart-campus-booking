class Resource:
    """Holds the details of one bookable resource (lab, projector, room)."""

    def __init__(self, resource_id, resource_code, name, resource_type, campus_id):
        self.resource_id = resource_id
        self.resource_code = resource_code
        self.name = name
        self.resource_type = resource_type
        self.campus_id = campus_id

    def __str__(self):
        return f"{self.resource_code} - {self.name}"