import tkinter as tk
from tkinter import ttk
from services.campus_service import get_all_campuses
from services.report_service import (get_comparison_report, get_all_bookings,
                                     get_resource_usage_all)


class OperatorFrame(tk.Frame):
    """Main screen for the system operator (all campuses)."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.user = app.current_user
        self.campuses = get_all_campuses()


        header = tk.Frame(self, bg="#1b5e20")
        header.pack(fill="x")
        tk.Label(header, text="System-wide view: All campuses  (System Operator)",
                 bg="#1b5e20", fg="white",
                 font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(header, text="Full access: bookings and resources across every campus.",
                 bg="#1b5e20", fg="white").pack(anchor="w", padx=10, pady=(0, 4))
        tk.Label(header, text=f"Logged in as: {self.user.full_name} ({self.user.role})",
                 bg="#1b5e20", fg="#c8e6c9").pack(anchor="w", padx=10, pady=(0, 8))


        bottom = tk.Frame(self)
        bottom.pack(side="bottom", fill="x", padx=10, pady=10)
        tk.Button(bottom, text="Back to campus list", width=18,
                  command=self.app.show_campus_select).pack(side="left")
        tk.Button(bottom, text="Log out", width=15,
                  command=self.app.show_login).pack(side="right")

        #TAB
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.compare_tab = tk.Frame(self.tabs)
        self.bookings_tab = tk.Frame(self.tabs)
        self.usage_tab = tk.Frame(self.tabs)
        self.tabs.add(self.compare_tab, text="Campus comparison")
        self.tabs.add(self.bookings_tab, text="All bookings")
        self.tabs.add(self.usage_tab, text="Resource usage")

        self.build_compare_tab()
        self.build_bookings_tab()
        self.build_usage_tab()

        self.refresh_all()
        self.tabs.bind("<<NotebookTabChanged>>", lambda event: self.refresh_all())


    def build_compare_tab(self):
        columns = ("campus", "total", "cancelled", "average", "busiest", "maxrule", "hours")
        self.compare_table = ttk.Treeview(self.compare_tab, columns=columns,
                                          show="headings", height=5)
        self.compare_table.heading("campus", text="Campus")
        self.compare_table.heading("total", text="Bookings")
        self.compare_table.heading("cancelled", text="Cancelled")
        self.compare_table.heading("average", text="Avg minutes")
        self.compare_table.heading("busiest", text="Busiest resource")
        self.compare_table.heading("maxrule", text="Rule: max minutes")
        self.compare_table.heading("hours", text="Rule: hours")
        self.compare_table.column("campus", width=110)
        self.compare_table.column("total", width=70)
        self.compare_table.column("cancelled", width=70)
        self.compare_table.column("average", width=80)
        self.compare_table.column("busiest", width=120)
        self.compare_table.column("maxrule", width=110)
        self.compare_table.column("hours", width=120)
        self.compare_table.pack(fill="x", padx=5, pady=10)

        self.insight_label = tk.Label(self.compare_tab, text="", justify="left",
                                      wraplength=780, font=("Arial", 10), fg="#1b5e20")
        self.insight_label.pack(anchor="w", padx=10, pady=5)

    def load_comparison(self):
        for row in self.compare_table.get_children():
            self.compare_table.delete(row)

        results = get_comparison_report()
        for item in results:
            self.compare_table.insert("", tk.END, values=(
                item["campus"], item["total_bookings"], item["cancelled"],
                item["average_duration"], item["busiest_resource"],
                item["max_minutes_rule"], item["opening_hours"]))


        if len(results) == 0:
            self.insight_label.config(text="")
            return

        busiest_campus = results[0]
        for item in results:
            if item["total_bookings"] > busiest_campus["total_bookings"]:
                busiest_campus = item

        longest_campus = results[0]
        for item in results:
            if item["average_duration"] > longest_campus["average_duration"]:
                longest_campus = item

        if busiest_campus["total_bookings"] == 0:
            self.insight_label.config(text="No bookings have been made yet.")
        else:
            self.insight_label.config(text=(
                f"Most bookings: {busiest_campus['campus']} "
                f"({busiest_campus['total_bookings']}).\n"
                f"Longest average booking: {longest_campus['campus']} "
                f"({longest_campus['average_duration']} min, with a "
                f"{longest_campus['max_minutes_rule']}-minute limit).\n"
                f"Compare the booking numbers with each campus's rules (last two columns) "
                f"to see how the policies affect usage."))


    def build_bookings_tab(self):
        top = tk.Frame(self.bookings_tab)
        top.pack(fill="x", padx=5, pady=8)
        tk.Label(top, text="Show campus:").pack(side="left")

        names = ["All campuses"]
        for campus in self.campuses:
            names.append(campus.name)
        self.filter_box = ttk.Combobox(top, values=names, state="readonly", width=20)
        self.filter_box.set("All campuses")
        self.filter_box.pack(side="left", padx=5)
        self.filter_box.bind("<<ComboboxSelected>>", lambda event: self.load_bookings())

        columns = ("id", "campus", "date", "start", "resource", "lecturer", "minutes", "status")
        self.bookings_table = ttk.Treeview(self.bookings_tab, columns=columns,
                                           show="headings", height=10)
        self.bookings_table.heading("id", text="Booking #")
        self.bookings_table.heading("campus", text="Campus")
        self.bookings_table.heading("date", text="Date")
        self.bookings_table.heading("start", text="Start")
        self.bookings_table.heading("resource", text="Resource")
        self.bookings_table.heading("lecturer", text="Lecturer")
        self.bookings_table.heading("minutes", text="Minutes")
        self.bookings_table.heading("status", text="Status")
        self.bookings_table.column("id", width=75)
        self.bookings_table.column("campus", width=100)
        self.bookings_table.column("date", width=90)
        self.bookings_table.column("start", width=60)
        self.bookings_table.column("resource", width=110)
        self.bookings_table.column("lecturer", width=150)
        self.bookings_table.column("minutes", width=65)
        self.bookings_table.column("status", width=80)
        self.bookings_table.pack(fill="both", expand=True, padx=5, pady=(0, 8))

    def load_bookings(self):
        for row in self.bookings_table.get_children():
            self.bookings_table.delete(row)


        chosen_id = None
        for campus in self.campuses:
            if campus.name == self.filter_box.get():
                chosen_id = campus.campus_id

        for b in get_all_bookings(chosen_id):
            if b["status"] == "cancelled":
                status = "Cancelled"
            else:
                status = "Active"
            self.bookings_table.insert("", tk.END, values=(
                b["booking_id"], b["campus_name"], b["booking_date"], b["start_time"],
                b["resource_code"], b["full_name"], b["duration_min"], status))


    def build_usage_tab(self):
        columns = ("campus", "code", "name", "uses", "minutes")
        self.usage_table = ttk.Treeview(self.usage_tab, columns=columns,
                                        show="headings", height=12)
        self.usage_table.heading("campus", text="Campus")
        self.usage_table.heading("code", text="Code")
        self.usage_table.heading("name", text="Resource")
        self.usage_table.heading("uses", text="Active bookings")
        self.usage_table.heading("minutes", text="Total minutes booked")
        self.usage_table.column("campus", width=120)
        self.usage_table.column("code", width=120)
        self.usage_table.column("name", width=180)
        self.usage_table.column("uses", width=120)
        self.usage_table.column("minutes", width=160)
        self.usage_table.pack(fill="both", expand=True, padx=5, pady=8)

    def load_usage(self):
        for row in self.usage_table.get_children():
            self.usage_table.delete(row)

        for r in get_resource_usage_all():
            self.usage_table.insert("", tk.END, values=(
                r["campus_name"], r["resource_code"], r["name"], r["uses"], r["minutes"]))


    def refresh_all(self):
        self.load_comparison()
        self.load_bookings()
        self.load_usage()