import tkinter as tk
from tkinter import messagebox
from services.campus_service import get_all_campuses
from rules.booking_rules import get_rule


class CampusSelectFrame(tk.Frame):
    """Screen where the user chooses which campus to work with."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        user = self.app.current_user

        tk.Label(self, text=f"Welcome, {user.full_name}",
                 font=("Arial", 14, "bold")).pack(pady=(30, 2))
        tk.Label(self, text=f"Role: {user.role}").pack(pady=(0, 20))

        tk.Label(self, text="Select a campus:", font=("Arial", 11)).pack()

        # campuses available
        all_campuses = get_all_campuses()
        self.campuses = []
        for campus in all_campuses:
            if user.can_view_all_campuses() or user.role == "lecturer":
                self.campuses.append(campus)
            elif campus.campus_id == user.campus_id:
                self.campuses.append(campus)       # admin: own campus only

        # The list of campuses
        self.listbox = tk.Listbox(self, height=5, width=30, exportselection=False)
        for campus in self.campuses:
            self.listbox.insert(tk.END, campus.name)
        self.listbox.pack(pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_policy)

        # Where the booking policy is displayed
        self.policy_label = tk.Label(self, text="Click a campus to see its booking policy.",
                                     wraplength=420, fg="blue")
        self.policy_label.pack(pady=10)

        tk.Button(self, text="Continue", width=20, command=self.choose_campus).pack(pady=(10, 5))

        if user.can_view_all_campuses():
            tk.Button(self, text="System-wide view (all campuses)", width=30,
                      command=self.app.open_operator_view).pack(pady=5)

        tk.Button(self, text="Log out", width=20, command=self.app.show_login).pack(pady=5)

    def get_selected_campus(self):
        """Return the Campus object that is highlighted, or None."""
        selection = self.listbox.curselection()
        if not selection:
            return None
        return self.campuses[selection[0]]

    def show_policy(self, event):
        """Show the booking policy of the highlighted campus."""
        campus = self.get_selected_campus()
        if campus is not None:
            rule = get_rule(campus.policy_key)
            self.policy_label.config(text=rule.describe())

    def choose_campus(self):
        """Called when 'Continue' is clicked."""
        campus = self.get_selected_campus()
        if campus is None:
            messagebox.showwarning("No campus", "Please select a campus first.")
            return
        self.app.select_campus(campus)