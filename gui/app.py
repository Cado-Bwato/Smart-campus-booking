import tkinter as tk
from tkinter import messagebox
from gui.login_window import LoginFrame, RegisterFrame
from gui.campus_select import CampusSelectFrame
from gui.lecturer_view import LecturerFrame
from gui.admin_view import AdminFrame
from gui.operator_view import OperatorFrame

class App:
    """Owns the window and decides which screen is showing."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Campus Resource Booking System")
        self.root.geometry("520x480")

        self.current_user = None       # who is logged in
        self.current_campus = None     # which campus they selected (next part)
        self.current_frame = None      # the screen showing now

        self.show_login()

    def show_frame(self, frame_class):
        """Remove the old screen and show a new one."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.root, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.current_user = None
        self.current_campus = None
        self.root.geometry("520x480")
        self.show_frame(LoginFrame)

    def show_register(self):
        self.show_frame(RegisterFrame)

    def login_success(self, user):
        """Called by the login screen after a correct login."""
        self.current_user = user
        self.show_frame(CampusSelectFrame)

    def show_campus_select(self):
        """Go back to the campus selection screen."""
        self.root.geometry("520x480")
        self.show_frame(CampusSelectFrame)

    def run(self):
        self.root.mainloop()

    def select_campus(self, campus):
        """Called when the user picks a campus. Opens the screen for their role."""
        self.current_campus = campus
        user = self.current_user

        if user.can_book():
            self.root.geometry("860x640")
            self.show_frame(LecturerFrame)
        elif user.can_manage_resources():
            self.root.geometry("860x640")
            self.show_frame(AdminFrame)
        elif user.can_view_all_campuses():
            self.open_operator_view()

    def open_operator_view(self):
        """Open the system-wide screen for the system operator."""
        self.root.geometry("860x640")
        self.show_frame(OperatorFrame)