from models.security import hash_password

class User:
    """Parent class. Every person who logs in is a User."""

    def __init__(self, user_id, username, password, full_name, role, campus_id=None):
        self.user_id = user_id
        self.username = username
        self._password = password
        self.full_name = full_name
        self.role = role
        self.campus_id = campus_id

    def check_password(self, typed_password):
        """Hash what was typed and compare it with the stored hash."""
        return self._password == hash_password(typed_password)

    def describe(self):
        print(f"{self.full_name} is a {self.role}")
    def can_book(self):
        return False

    def can_manage_resources(self):
        return False

    def can_view_all_campuses(self):
        return False

class Lecturer(User):
    def __init__(self, user_id, username, password, full_name, campus_id=None):
        super().__init__(user_id, username, password, full_name, "lecturer", campus_id)

    def can_book(self):
        return True


class CampusAdmin(User):
    def __init__(self, user_id, username, password, full_name, campus_id):
        super().__init__(user_id, username, password, full_name, "admin", campus_id)

    def can_manage_resources(self):
        return True


class SystemOperator(User):
    def __init__(self, user_id, username, password, full_name):
        super().__init__(user_id, username, password, full_name, "operator")

    def can_view_all_campuses(self):
        return True
