import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from services.resource_service import (get_resources_by_campus, add_resource,
                                       update_resource, remove_resource)
from services.booking_service import get_booked_slots
from services.report_service import get_campus_report, get_usage_trend, get_campus_bookings
from rules.booking_rules import get_rule


class AdminFrame(tk.Frame):
    """Main screen for a campus administrator."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.user = app.current_user
        self.campus = app.current_campus
        rule = get_rule(self.campus.policy_key)

        # ---------- Header ----------
        header = tk.Frame(self, bg="#4a148c")
        header.pack(fill="x")
        tk.Label(header, text=f"Active campus: {self.campus.name}  (Administrator)",
                 bg="#4a148c", fg="white",
                 font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(header, text=rule.describe(), bg="#4a148c", fg="white").pack(
            anchor="w", padx=10, pady=(0, 4))
        tk.Label(header, text=f"Logged in as: {self.user.full_name} ({self.user.role})",
                 bg="#4a148c", fg="#e1bee7").pack(anchor="w", padx=10, pady=(0, 8))

        # ---------- Bottom buttons ----------
        bottom = tk.Frame(self)
        bottom.pack(side="bottom", fill="x", padx=10, pady=10)
        tk.Button(bottom, text="Log out", width=15,
                  command=self.app.show_login).pack(side="right")

        # ---------- Tabs ----------
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.resources_tab = tk.Frame(self.tabs)
        self.bookings_tab = tk.Frame(self.tabs)
        self.reports_tab = tk.Frame(self.tabs)
        self.tabs.add(self.resources_tab, text="Resources")
        self.tabs.add(self.bookings_tab, text="Campus bookings")
        self.tabs.add(self.reports_tab, text="Reports & usage")

        self.build_resources_tab()
        self.build_bookings_tab()
        self.build_reports_tab()

        self.refresh_all()

        # Reload the data whenever the admin clicks a different tab
        self.tabs.bind("<<NotebookTabChanged>>", lambda event: self.refresh_all())

    # =====================================================
    #  TAB 1: Resources
    # =====================================================
    def build_resources_tab(self):
        columns = ("code", "name", "type", "today")
        self.res_table = ttk.Treeview(self.resources_tab, columns=columns,
                                      show="headings", height=6, selectmode="browse")
        self.res_table.heading("code", text="Code")
        self.res_table.heading("name", text="Resource")
        self.res_table.heading("type", text="Type")
        self.res_table.heading("today", text="Availability today")
        self.res_table.column("code", width=110)
        self.res_table.column("name", width=150)
        self.res_table.column("type", width=130)
        self.res_table.column("today", width=360)
        self.res_table.pack(fill="both", expand=True, padx=5, pady=8)
        self.res_table.bind("<<TreeviewSelect>>", self.fill_form_from_selection)

        # The form
        form = tk.LabelFrame(self.resources_tab, text="Add or edit a resource")
        form.pack(fill="x", padx=5, pady=5)

        tk.Label(form, text="Code:").grid(row=0, column=0, padx=5, pady=6, sticky="e")
        self.code_entry = tk.Entry(form, width=16)
        self.code_entry.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Name:").grid(row=0, column=2, padx=5, sticky="e")
        self.name_entry = tk.Entry(form, width=20)
        self.name_entry.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Type:").grid(row=0, column=4, padx=5, sticky="e")
        self.type_box = ttk.Combobox(form, width=20, values=(
            "Computer Lab", "Projector", "Seminar Room", "Presentation Equipment"))
        self.type_box.grid(row=0, column=5, padx=5)

        # Buttons
        buttons = tk.Frame(self.resources_tab)
        buttons.pack(pady=8)
        tk.Button(buttons, text="Add resource", width=14, bg="#2e7d32", fg="white",
                  command=self.do_add).pack(side="left", padx=5)
        tk.Button(buttons, text="Update selected", width=14,
                  command=self.do_update).pack(side="left", padx=5)
        tk.Button(buttons, text="Remove selected", width=14, bg="#c62828", fg="white",
                  command=self.do_remove).pack(side="left", padx=5)
        tk.Button(buttons, text="Clear form", width=10,
                  command=self.clear_form).pack(side="left", padx=5)

    def get_selected_resource_id(self):
        """Return the ID of the highlighted resource, or None."""
        selection = self.res_table.selection()
        if not selection:
            return None
        return int(selection[0])

    def fill_form_from_selection(self, event):
        """When a row is clicked, copy its details into the form."""
        selection = self.res_table.selection()
        if not selection:
            return
        values = self.res_table.item(selection[0], "values")
        self.code_entry.delete(0, tk.END)
        self.code_entry.insert(0, values[0])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        self.type_box.set(values[2])

    def clear_form(self):
        self.code_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.type_box.set("")
        for item in self.res_table.selection():
            self.res_table.selection_remove(item)

    def do_add(self):
        success, message = add_resource(self.code_entry.get(), self.name_entry.get(),
                                        self.type_box.get(), self.campus.campus_id)
        if success:
            messagebox.showinfo("Added", message)
            self.clear_form()
            self.refresh_all()
        else:
            messagebox.showerror("Cannot add", message)

    def do_update(self):
        resource_id = self.get_selected_resource_id()
        if resource_id is None:
            messagebox.showwarning("No resource", "Please click a resource in the table first.")
            return

        success, message = update_resource(resource_id, self.name_entry.get(),
                                           self.type_box.get())
        if success:
            messagebox.showinfo("Updated", message + "\n(The code cannot be changed.)")
            self.refresh_all()
        else:
            messagebox.showerror("Cannot update", message)

    def do_remove(self):
        resource_id = self.get_selected_resource_id()
        if resource_id is None:
            messagebox.showwarning("No resource", "Please click a resource in the table first.")
            return

        if not messagebox.askyesno("Confirm", "Remove the selected resource?"):
            return

        success, message = remove_resource(resource_id)
        if success:
            messagebox.showinfo("Removed", message)
            self.clear_form()
            self.refresh_all()
        else:
            messagebox.showerror("Cannot remove", message)

    # =====================================================
    #  TAB 2: Campus bookings
    # =====================================================
    def build_bookings_tab(self):
        columns = ("id", "date", "start", "resource", "lecturer", "minutes", "status")
        self.bookings_table = ttk.Treeview(self.bookings_tab, columns=columns,
                                           show="headings", height=12)
        self.bookings_table.heading("id", text="Booking #")
        self.bookings_table.heading("date", text="Date")
        self.bookings_table.heading("start", text="Start")
        self.bookings_table.heading("resource", text="Resource")
        self.bookings_table.heading("lecturer", text="Lecturer")
        self.bookings_table.heading("minutes", text="Minutes")
        self.bookings_table.heading("status", text="Status")
        self.bookings_table.column("id", width=80)
        self.bookings_table.column("date", width=100)
        self.bookings_table.column("start", width=70)
        self.bookings_table.column("resource", width=120)
        self.bookings_table.column("lecturer", width=180)
        self.bookings_table.column("minutes", width=70)
        self.bookings_table.column("status", width=90)
        self.bookings_table.pack(fill="both", expand=True, padx=5, pady=8)

    # =====================================================
    #  TAB 3: Reports and usage
    # =====================================================
    def build_reports_tab(self):
        self.summary_label = tk.Label(self.reports_tab, text="", justify="left",
                                      font=("Arial", 11))
        self.summary_label.pack(anchor="w", padx=10, pady=8)

        top_frame = tk.LabelFrame(self.reports_tab, text="Most frequently used resources")
        top_frame.pack(fill="x", padx=5, pady=4)
        self.top_table = ttk.Treeview(top_frame, columns=("resource", "uses", "minutes"),
                                      show="headings", height=4)
        self.top_table.heading("resource", text="Resource")
        self.top_table.heading("uses", text="Bookings")
        self.top_table.heading("minutes", text="Total minutes booked")
        self.top_table.column("resource", width=300)
        self.top_table.column("uses", width=100)
        self.top_table.column("minutes", width=180)
        self.top_table.pack(fill="x", padx=5, pady=5)

        trend_frame = tk.LabelFrame(self.reports_tab, text="Usage trend (bookings per date)")
        trend_frame.pack(fill="x", padx=5, pady=4)
        self.trend_table = ttk.Treeview(trend_frame, columns=("date", "total"),
                                        show="headings", height=4)
        self.trend_table.heading("date", text="Date")
        self.trend_table.heading("total", text="Bookings")
        self.trend_table.column("date", width=200)
        self.trend_table.column("total", width=100)
        self.trend_table.pack(fill="x", padx=5, pady=5)

    # =====================================================
    #  Loading data into the tables
    # =====================================================
    def refresh_all(self):
        self.load_resources()
        self.load_bookings()
        self.load_reports()

    def clear_table(self, table):
        for row in table.get_children():
            table.delete(row)

    def load_resources(self):
        self.clear_table(self.res_table)
        today = date.today().isoformat()

        for resource in get_resources_by_campus(self.campus.campus_id):
            slots = get_booked_slots(resource.resource_id, today)
            if len(slots) == 0:
                availability = "Available all day"
            else:
                times = []
                for start, end in slots:
                    times.append(f"{start}-{end}")
                availability = "Booked: " + ", ".join(times)

            self.res_table.insert("", tk.END, iid=str(resource.resource_id),
                                  values=(resource.resource_code, resource.name,
                                          resource.resource_type, availability))

    def load_bookings(self):
        self.clear_table(self.bookings_table)
        for b in get_campus_bookings(self.campus.campus_id):
            if b["status"] == "cancelled":
                status = "Cancelled"
            else:
                status = "Active"
            self.bookings_table.insert("", tk.END,
                                       values=(b["booking_id"], b["booking_date"],
                                               b["start_time"], b["resource_code"],
                                               b["full_name"], b["duration_min"], status))

    def load_reports(self):
        report = get_campus_report(self.campus.campus_id)
        self.summary_label.config(text=(
            f"Total active bookings: {report['total_bookings']}\n"
            f"Cancelled bookings: {report['cancelled_bookings']}\n"
            f"Average booking duration: {report['average_duration']} minutes"))

        self.clear_table(self.top_table)
        for r in report["top_resources"]:
            self.top_table.insert("", tk.END,
                                  values=(f"{r['resource_code']} - {r['name']}",
                                          r["uses"], r["minutes"]))

        self.clear_table(self.trend_table)
        for row in get_usage_trend(self.campus.campus_id):
            self.trend_table.insert("", tk.END, values=(row["booking_date"], row["total"]))