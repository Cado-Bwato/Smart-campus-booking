import tkinter as tk
from tkinter import messagebox
from services.auth_service import login, register_lecturer


class LoginFrame(tk.Frame):
    """The login screen."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Smart Campus Booking System",
                 font=("Arial", 16, "bold")).pack(pady=(40, 5))
        tk.Label(self, text="Please log in", font=("Arial", 11)).pack(pady=(0, 20))

        tk.Label(self, text="Username").pack()
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=(0, 10))

        tk.Label(self, text="Password").pack()
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=(0, 10))
        self.password_entry.bind("<Return>", lambda event: self.do_login())

        tk.Button(self, text="Login", width=20, command=self.do_login).pack(pady=(15, 5))
        tk.Button(self, text="Register (Lecturers)", width=20,
                  command=self.app.show_register).pack()

    def do_login(self):
        """Called when the Login button is clicked."""
        user, message = login(self.username_entry.get(), self.password_entry.get())

        if user is None:
            messagebox.showerror("Login failed", message)
        else:
            self.app.login_success(user)


class RegisterFrame(tk.Frame):
    """The screen where a lecturer creates an account."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Register a Lecturer Account",
                 font=("Arial", 16, "bold")).pack(pady=(30, 20))

        tk.Label(self, text="Full name").pack()
        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.pack(pady=(0, 10))

        tk.Label(self, text="Username").pack()
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=(0, 10))

        tk.Label(self, text="Password").pack()
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=(0, 10))

        tk.Label(self, text="Confirm password").pack()
        self.confirm_entry = tk.Entry(self, width=30, show="*")
        self.confirm_entry.pack(pady=(0, 10))

        tk.Button(self, text="Create account", width=20,
                  command=self.do_register).pack(pady=(15, 5))
        tk.Button(self, text="Back to login", width=20,
                  command=self.app.show_login).pack()

    def do_register(self):
        """Called when 'Create account' is clicked."""
        if self.password_entry.get() != self.confirm_entry.get():
            messagebox.showerror("Error", "The two passwords do not match.")
            return

        success, message = register_lecturer(self.username_entry.get(),
                                             self.password_entry.get(),
                                             self.name_entry.get())
        if success:
            messagebox.showinfo("Success", message)
            self.app.show_login()
        else:
            messagebox.showerror("Error", message)