"""
Dashboard View: Modern SaaS Light themed dashboard
Includes:
- High level welcome header
- 4 Quick-Stats SaaS metric cards with badge trends
- Embedded interactive Matplotlib charts (Circulation doughnut + Genre distribution)
- Active Circulations & Overdue alert table with color tags and fine calculation
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from ui_theme import Theme
from ui_charts import AnalyticsCharts

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db, app_instance, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self.app = app_instance
        
        self._build_ui()

    def _build_ui(self):
        # 1. Page Header with SaaS greeting and date
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        today_str = date.today().strftime("%A, %B %d, %Y")
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        
        title = ctk.CTkLabel(
            title_box,
            text="Dashboard Overview",
            font=(Theme.FONT_FAMILY, 24, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_box,
            text=f"Welcome back, {self.app.current_user or 'Administrator'} • {today_str}",
            font=(Theme.FONT_FAMILY, 12),
            text_color=Theme.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))
        
        # Right action buttons (Quick Refresh)
        btn_refresh = ctk.CTkButton(
            header,
            text="🔄 Refresh Data",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.BG_CARD,
            text_color=Theme.PRIMARY,
            hover_color=Theme.SURFACE_MUTED,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            corner_radius=8,
            height=36,
            command=self.refresh
        )
        btn_refresh.pack(side="right")

        # 2. Key Metric Stat Cards
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.pack(fill="x", pady=(0, 18))
        self._render_metric_cards()

        # 3. Analytics Chart Card
        self.chart_view = AnalyticsCharts(self, self.db)
        self.chart_view.pack(fill="x", pady=(0, 18))

        # 4. Active Circulation & Overdue Tracker Table
        tracker_card = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        tracker_card.pack(fill="both", expand=True)

        table_header = ctk.CTkFrame(tracker_card, fg_color="transparent")
        table_header.pack(fill="x", padx=16, pady=(14, 10))

        tbl_title = ctk.CTkLabel(
            table_header,
            text="⏳ Active Circulations & Overdue Tracker",
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        tbl_title.pack(side="left")

        tbl_sub = ctk.CTkLabel(
            table_header,
            text="Real-time monitor with automated fine calculations (Rs. 2/day)",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.TEXT_MUTED
        )
        tbl_sub.pack(side="right")

        # Treeview Container
        tree_container = tk.Frame(tracker_card, bg="#FFFFFF")
        tree_container.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        cols = ("Book ID", "Title", "Member ID", "Member Name", "Issue Date", "Due Date", "Days Remaining / Status")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", style="Modern.Treeview")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=110)
        self.tree.column("Title", anchor="w", width=190)
        self.tree.column("Member Name", anchor="w", width=140)
        self.tree.column("Days Remaining / Status", anchor="center", width=180)

        sb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Tags for overdue and normal rows
        self.tree.tag_configure("overdue", background=Theme.OVERDUE_BG, foreground=Theme.OVERDUE_FG)
        self.tree.tag_configure("normal", background="#FFFFFF", foreground=Theme.TEXT_PRIMARY)

        self._populate_issues_table()

    def _render_metric_cards(self):
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        stats = self.db.get_stats()
        cards_config = [
            ("Total Inventory", stats["total_books"], "📚", Theme.PRIMARY, Theme.PRIMARY_LIGHT, "Registered titles"),
            ("Available for Rent", stats["available_books"], "✅", Theme.SUCCESS, Theme.SUCCESS_LIGHT, "In library shelves"),
            ("Currently Issued", stats["issued_books"], "⏳", Theme.WARNING, Theme.WARNING_LIGHT, "Out on loan"),
            ("Active Members", stats["total_members"], "👥", Theme.PURPLE, Theme.PURPLE_LIGHT, "Patron directory"),
        ]

        for idx, (title, val, icon, color, bg_light, sub) in enumerate(cards_config):
            card = ctk.CTkFrame(
                self.stats_container,
                fg_color=Theme.BG_CARD,
                corner_radius=12,
                border_width=1,
                border_color=Theme.BORDER_LIGHT
            )
            card.grid(row=0, column=idx, padx=6 if idx > 0 else (0, 6), sticky="nsew")
            self.stats_container.grid_columnconfigure(idx, weight=1)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=16)

            top_row = ctk.CTkFrame(inner, fg_color="transparent")
            top_row.pack(fill="x")

            lbl_title = ctk.CTkLabel(
                top_row,
                text=title,
                font=(Theme.FONT_FAMILY, 12, "bold"),
                text_color=Theme.TEXT_SECONDARY
            )
            lbl_title.pack(side="left")

            icon_badge = ctk.CTkLabel(
                top_row,
                text=icon,
                font=(Theme.FONT_FAMILY, 14),
                fg_color=bg_light,
                text_color=color,
                corner_radius=6,
                width=28,
                height=28
            )
            icon_badge.pack(side="right")

            lbl_val = ctk.CTkLabel(
                inner,
                text=str(val),
                font=(Theme.FONT_FAMILY, 28, "bold"),
                text_color=Theme.TEXT_PRIMARY
            )
            lbl_val.pack(anchor="w", pady=(8, 2))

            lbl_sub = ctk.CTkLabel(
                inner,
                text=sub,
                font=(Theme.FONT_FAMILY, 11),
                text_color=Theme.TEXT_MUTED
            )
            lbl_sub.pack(anchor="w")

    def _populate_issues_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        today = date.today()
        issues = self.db.get_active_issues()

        if not issues:
            self.tree.insert("", "end", values=("No books currently issued", "-", "-", "-", "-", "-", "All books in shelf"), tags=("normal",))
            return

        for iss in issues:
            due_d = datetime.strptime(iss["due_date"], "%Y-%m-%d").date()
            days_diff = (due_d - today).days
            if days_diff < 0:
                status_text = f"OVERDUE ({abs(days_diff)}d late • Fine: Rs.{abs(days_diff)*2})"
                tag = "overdue"
            elif days_diff == 0:
                status_text = "Due Today"
                tag = "overdue"
            else:
                status_text = f"{days_diff} days remaining"
                tag = "normal"

            self.tree.insert("", "end", values=(
                iss.get("book_id"),
                iss.get("book_title"),
                iss.get("member_id"),
                iss.get("member_name"),
                iss.get("issue_date"),
                iss.get("due_date"),
                status_text
            ), tags=(tag,))

    def refresh(self):
        self._render_metric_cards()
        self.chart_view.refresh()
        self._populate_issues_table()
        self.app.set_status("Dashboard refreshed with latest circulation data.")
