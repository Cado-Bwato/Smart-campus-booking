import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from services.resource_service import get_resources_by_campus
from services.booking_service import (create_booking, get_booked_slots,
                                      get_user_bookings, cancel_booking)
from rules.booking_rules import get_rule


class LecturerFrame(tk.Frame):
    """Main screen for a lecturer working at one campus."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.user = app.current_user
        self.campus = app.current_campus
        rule = get_rule(self.campus.policy_key)


        header = tk.Frame(self, bg="#1f4e79")
        header.pack(fill="x")
        tk.Label(header, text=f"Active campus: {self.campus.name}",
                 bg="#1f4e79", fg="white",
                 font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(header, text=rule.describe(), bg="#1f4e79", fg="white").pack(
            anchor="w", padx=10, pady=(0, 4))
        tk.Label(header, text=f"Logged in as: {self.user.full_name} ({self.user.role})",
                 bg="#1f4e79", fg="#cfe2f3").pack(anchor="w", padx=10, pady=(0, 8))


        bottom = tk.Frame(self)
        bottom.pack(side="bottom", fill="x", padx=10, pady=10)
        tk.Button(bottom, text="Change campus", width=15,
                  command=self.app.show_campus_select).pack(side="left")
        tk.Button(bottom, text="Log out", width=15,
                  command=self.app.show_login).pack(side="right")


        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.book_tab = tk.Frame(self.tabs)
        self.active_tab = tk.Frame(self.tabs)
        self.past_tab = tk.Frame(self.tabs)
        self.tabs.add(self.book_tab, text="Book a resource")
        self.tabs.add(self.active_tab, text="My active bookings")
        self.tabs.add(self.past_tab, text="Past bookings")

        self.build_book_tab()
        self.build_active_tab()
        self.build_past_tab()

        self.refresh_all()

   #TAB1
    def build_book_tab(self):
        top = tk.Frame(self.book_tab)
        top.pack(fill="x", padx=5, pady=8)
        tk.Label(top, text="Date (YYYY-MM-DD):").pack(side="left")
        self.date_entry = tk.Entry(top, width=12)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.pack(side="left", padx=5)
        tk.Button(top, text="Refresh availability",
                  command=self.load_resources).pack(side="left", padx=5)

        columns = ("code", "name", "type", "availability")
        self.table = ttk.Treeview(self.book_tab, columns=columns,
                                  show="headings", height=7, selectmode="browse")
        self.table.heading("code", text="Code")
        self.table.heading("name", text="Resource")
        self.table.heading("type", text="Type")
        self.table.heading("availability", text="Availability on this date")
        self.table.column("code", width=110)
        self.table.column("name", width=150)
        self.table.column("type", width=120)
        self.table.column("availability", width=380)
        self.table.pack(fill="both", expand=True, padx=5)

        # Booking form
        form = tk.LabelFrame(self.book_tab, text="Make a booking for the selected resource")
        form.pack(fill="x", padx=5, pady=10)

        tk.Label(form, text="Start time (HH:MM):").grid(row=0, column=0, padx=5, pady=8)
        self.start_entry = tk.Entry(form, width=8)
        self.start_entry.insert(0, "09:00")
        self.start_entry.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Duration (minutes):").grid(row=0, column=2, padx=5)
        self.duration_entry = tk.Entry(form, width=8)
        self.duration_entry.insert(0, "60")
        self.duration_entry.grid(row=0, column=3, padx=5)

        tk.Button(form, text="Book", width=12, bg="#2e7d32", fg="white",
                  command=self.do_booking).grid(row=0, column=4, padx=15)

    def load_resources(self):
        """Fill the table with this campus's resources and their availability."""
        date_text = self.date_entry.get().strip()

        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Please enter the date as YYYY-MM-DD.")
            return

        for row in self.table.get_children():
            self.table.delete(row)

        resources = get_resources_by_campus(self.campus.campus_id)
        for resource in resources:
            slots = get_booked_slots(resource.resource_id, date_text)
            if len(slots) == 0:
                availability = "Available all day"
            else:
                times = []
                for start, end in slots:
                    times.append(f"{start}-{end}")
                availability = "Booked: " + ", ".join(times)

            self.table.insert("", tk.END, iid=str(resource.resource_id),
                              values=(resource.resource_code, resource.name,
                                      resource.resource_type, availability))

    def do_booking(self):
        """Called when the Book button is clicked."""
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("No resource", "Please click a resource in the table first.")
            return

        resource_id = int(selection[0])

        success, message = create_booking(
            self.user.user_id,
            resource_id,
            self.campus.campus_id,
            self.date_entry.get().strip(),
            self.start_entry.get().strip(),
            self.duration_entry.get().strip()
        )

        if success:
            messagebox.showinfo("Booked", message)
            self.refresh_all()
        else:
            messagebox.showerror("Booking refused", message)

    #TAB2
    def build_active_tab(self):
        columns = ("id", "campus", "resource", "date", "start", "duration")
        self.active_table = ttk.Treeview(self.active_tab, columns=columns,
                                         show="headings", height=10, selectmode="browse")
        self.active_table.heading("id", text="Booking #")
        self.active_table.heading("campus", text="Campus")
        self.active_table.heading("resource", text="Resource")
        self.active_table.heading("date", text="Date")
        self.active_table.heading("start", text="Start")
        self.active_table.heading("duration", text="Minutes")
        self.active_table.column("id", width=80)
        self.active_table.column("campus", width=120)
        self.active_table.column("resource", width=140)
        self.active_table.column("date", width=110)
        self.active_table.column("start", width=80)
        self.active_table.column("duration", width=80)
        self.active_table.pack(fill="both", expand=True, padx=5, pady=8)

        tk.Button(self.active_tab, text="Cancel selected booking", width=25,
                  bg="#c62828", fg="white", command=self.do_cancel).pack(pady=(0, 8))

    def do_cancel(self):
        """Called when 'Cancel selected booking' is clicked."""
        selection = self.active_table.selection()
        if not selection:
            messagebox.showwarning("No booking", "Please select a booking to cancel.")
            return

        booking_id = int(selection[0])
        if not messagebox.askyesno("Confirm", f"Cancel booking #{booking_id}?"):
            return

        success, message = cancel_booking(booking_id, self.user.user_id)
        if success:
            messagebox.showinfo("Cancelled", message)
            self.refresh_all()
        else:
            messagebox.showerror("Cannot cancel", message)


    def build_past_tab(self):
        columns = ("id", "campus", "resource", "date", "start", "duration", "status")
        self.past_table = ttk.Treeview(self.past_tab, columns=columns,
                                       show="headings", height=10)
        self.past_table.heading("id", text="Booking #")
        self.past_table.heading("campus", text="Campus")
        self.past_table.heading("resource", text="Resource")
        self.past_table.heading("date", text="Date")
        self.past_table.heading("start", text="Start")
        self.past_table.heading("duration", text="Minutes")
        self.past_table.heading("status", text="Status")
        self.past_table.column("id", width=80)
        self.past_table.column("campus", width=110)
        self.past_table.column("resource", width=130)
        self.past_table.column("date", width=100)
        self.past_table.column("start", width=70)
        self.past_table.column("duration", width=70)
        self.past_table.column("status", width=90)
        self.past_table.pack(fill="both", expand=True, padx=5, pady=8)


    def refresh_all(self):
        """Reload all three tabs from the database."""
        self.load_resources()
        self.load_my_bookings()

    def load_my_bookings(self):
        """Fill the Active and Past tables."""
        for row in self.active_table.get_children():
            self.active_table.delete(row)
        for row in self.past_table.get_children():
            self.past_table.delete(row)

        active, past = get_user_bookings(self.user.user_id)

        for b in active:
            self.active_table.insert("", tk.END, iid=str(b["booking_id"]),
                                     values=(b["booking_id"], b["campus_name"],
                                             b["resource_code"], b["booking_date"],
                                             b["start_time"], b["duration_min"]))

        for b in past:
            if b["status"] == "cancelled":
                status = "Cancelled"
            else:
                status = "Completed"
            self.past_table.insert("", tk.END, iid=str(b["booking_id"]),
                                   values=(b["booking_id"], b["campus_name"],
                                           b["resource_code"], b["booking_date"],
                                           b["start_time"], b["duration_min"], status))