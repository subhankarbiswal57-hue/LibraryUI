"""
Issue & Return Circulation View: SaaS Workflow
Features:
- Side-by-side dedicated Issue and Return transaction cards
- Automated 14-day loan term calculation with calendar indicator
- Real-time late fine calculator (Rs. 2/day past due)
- Active Circulations tracking table with distinct Overdue visual tags
- Safe return flow with confirmation dialogs
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
from ui_theme import Theme
from ui_dialogs import ConfirmModal, AlertModal

class IssueReturnView(ctk.CTkFrame):
    def __init__(self, parent, db, app_instance, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self.app = app_instance
        self.sort_directions = {}

        self._build_ui()

    def _build_ui(self):
        # 1. Page Header
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 14))

        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.pack(side="left")

        lbl_title = ctk.CTkLabel(
            title_box,
            text="Circulation Desk (Issue & Return)",
            font=(Theme.FONT_FAMILY, 24, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        lbl_title.pack(anchor="w")

        lbl_subtitle = ctk.CTkLabel(
            title_box,
            text="Issue books to patrons, process check-ins, and inspect late fines",
            font=(Theme.FONT_FAMILY, 12),
            text_color=Theme.TEXT_SECONDARY
        )
        lbl_subtitle.pack(anchor="w", pady=(2, 0))

        # 2. Split Transaction Cards: Issue (Left) & Return (Right)
        panels_container = ctk.CTkFrame(self, fg_color="transparent")
        panels_container.pack(fill="x", pady=(0, 16))

        # Panel 1: Issue Book Form Card
        p1 = ctk.CTkFrame(
            panels_container,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        p1.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._build_issue_panel(p1)

        # Panel 2: Return Book Form Card
        p2 = ctk.CTkFrame(
            panels_container,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        p2.pack(side="right", fill="both", expand=True, padx=(8, 0))
        self._build_return_panel(p2)

        # 3. Active Circulations Table Card
        table_card = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        table_card.pack(fill="both", expand=True)

        t_head = ctk.CTkFrame(table_card, fg_color="transparent")
        t_head.pack(fill="x", padx=16, pady=(12, 8))

        lbl_t_title = ctk.CTkLabel(
            t_head,
            text="📋 Active Checked-Out Books",
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        lbl_t_title.pack(side="left")

        lbl_t_hint = ctk.CTkLabel(
            t_head,
            text="🔴 Red highlight indicates overdue loan past 14-day threshold",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.DANGER
        )
        lbl_t_hint.pack(side="right")

        tree_wrapper = tk.Frame(table_card, bg="#FFFFFF")
        tree_wrapper.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        cols = ("Book ID", "Title", "Member ID", "Member Name", "Issue Date", "Due Date", "Days Remaining / Overdue")
        self.issue_tree = ttk.Treeview(tree_wrapper, columns=cols, show="headings", style="Modern.Treeview")

        for c in cols:
            self.issue_tree.heading(c, text=c, command=lambda _c=c: self.sort_column(_c))
            self.issue_tree.column(c, anchor="center", width=110)

        self.issue_tree.column("Title", anchor="w", width=200)
        self.issue_tree.column("Member Name", anchor="w", width=150)
        self.issue_tree.column("Days Remaining / Overdue", anchor="center", width=180)

        sb = ttk.Scrollbar(tree_wrapper, orient="vertical", command=self.issue_tree.yview)
        self.issue_tree.configure(yscrollcommand=sb.set)
        self.issue_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.issue_tree.tag_configure("overdue", background=Theme.OVERDUE_BG, foreground=Theme.OVERDUE_FG)
        self.issue_tree.tag_configure("normal", background="#FFFFFF", foreground=Theme.TEXT_PRIMARY)

        self.refresh_data()

    def _build_issue_panel(self, container):
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            title_row,
            text="📤 Issue Book on Loan",
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.PRIMARY
        ).pack(side="left")

        term_badge = ctk.CTkLabel(
            title_row,
            text="Standard: 14 Days",
            font=(Theme.FONT_FAMILY, 10, "bold"),
            fg_color=Theme.PRIMARY_LIGHT,
            text_color=Theme.PRIMARY,
            corner_radius=4,
            padx=6,
            pady=2
        )
        term_badge.pack(side="right")

        # Book Combobox
        ctk.CTkLabel(inner, text="Select Available Book *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.cb_issue_book = ctk.CTkOptionMenu(
            inner,
            values=["No available books"],
            height=32,
            font=(Theme.FONT_FAMILY, 11),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            button_color=Theme.BORDER_LIGHT,
            corner_radius=6
        )
        self.cb_issue_book.pack(fill="x", pady=(3, 10))

        # Member Combobox
        ctk.CTkLabel(inner, text="Select Registered Member *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.cb_issue_member = ctk.CTkOptionMenu(
            inner,
            values=["No registered members"],
            height=32,
            font=(Theme.FONT_FAMILY, 11),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            button_color=Theme.BORDER_LIGHT,
            corner_radius=6
        )
        self.cb_issue_member.pack(fill="x", pady=(3, 10))

        # Dates Preview card
        self.date_box = ctk.CTkFrame(inner, fg_color=Theme.SURFACE_MUTED, corner_radius=8)
        self.date_box.pack(fill="x", pady=(2, 12))

        date_inner = ctk.CTkFrame(self.date_box, fg_color="transparent")
        date_inner.pack(fill="x", padx=12, pady=8)

        today = date.today()
        due = today + timedelta(days=14)

        self.lbl_iss_date = ctk.CTkLabel(
            date_inner,
            text=f"📅 Issue: {today.strftime('%b %d, %Y')}",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.TEXT_SECONDARY
        )
        self.lbl_iss_date.pack(side="left")

        self.lbl_due_date = ctk.CTkLabel(
            date_inner,
            text=f"⏰ Due: {due.strftime('%b %d, %Y')}",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.SUCCESS_TEXT
        )
        self.lbl_due_date.pack(side="right")

        # Submit button
        btn_issue = ctk.CTkButton(
            inner,
            text="Complete Checkout",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self.action_issue_book
        )
        btn_issue.pack(fill="x")

    def _build_return_panel(self, container):
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            title_row,
            text="📥 Return Book & Check-In",
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.WARNING
        ).pack(side="left")

        policy_badge = ctk.CTkLabel(
            title_row,
            text="Fine: Rs. 2 / day",
            font=(Theme.FONT_FAMILY, 10, "bold"),
            fg_color=Theme.WARNING_LIGHT,
            text_color=Theme.WARNING_TEXT,
            corner_radius=4,
            padx=6,
            pady=2
        )
        policy_badge.pack(side="right")

        ctk.CTkLabel(inner, text="Select Currently Checked-Out Book *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.cb_return_book = ctk.CTkOptionMenu(
            inner,
            values=["No active checkouts"],
            height=32,
            font=(Theme.FONT_FAMILY, 11),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            button_color=Theme.BORDER_LIGHT,
            corner_radius=6,
            command=self._on_return_selection_changed
        )
        self.cb_return_book.pack(fill="x", pady=(3, 10))

        # Real-time fine inspection box
        self.fine_box = ctk.CTkFrame(inner, fg_color=Theme.SURFACE_MUTED, corner_radius=8)
        self.fine_box.pack(fill="x", pady=(2, 12))

        fine_inner = ctk.CTkFrame(self.fine_box, fg_color="transparent")
        fine_inner.pack(fill="x", padx=12, pady=8)

        self.lbl_return_info = ctk.CTkLabel(
            fine_inner,
            text="Select an issued book above to preview fine status",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        )
        self.lbl_return_info.pack(fill="x")

        # Submit Return button
        btn_return = ctk.CTkButton(
            inner,
            text="Process Return & Check-In",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_TEXT,
            corner_radius=8,
            height=36,
            command=self.action_return_book
        )
        btn_return.pack(fill="x")

    def _on_return_selection_changed(self, selection):
        if not selection or selection == "No active checkouts":
            self.lbl_return_info.configure(text="No active checkouts currently selected.")
            return

        book_id = selection.split("|")[0].strip()
        active = self.db.get_active_issues()
        iss = next((i for i in active if i["book_id"] == book_id), None)
        if not iss:
            return

        today = date.today()
        due_d = datetime.strptime(iss["due_date"], "%Y-%m-%d").date()
        days_late = (today - due_d).days

        if days_late > 0:
            fine = days_late * 2
            self.lbl_return_info.configure(
                text=f"⚠️ OVERDUE by {days_late} days. Pending Late Fine: Rs. {fine}",
                text_color=Theme.DANGER
            )
        elif days_late == 0:
            self.lbl_return_info.configure(
                text="ℹ️ Book is due today. No late fine applied.",
                text_color=Theme.WARNING
            )
        else:
            self.lbl_return_info.configure(
                text=f"✅ On time ({abs(days_late)} days remaining before due date). Zero fine.",
                text_color=Theme.SUCCESS_TEXT
            )

    def refresh_data(self):
        # Update available books combobox
        avail = [f"{b['id']} | {b['title']}" for b in self.db.get_books() if b.get("status") == "Available"]
        if avail:
            self.cb_issue_book.configure(values=avail)
            self.cb_issue_book.set(avail[0])
        else:
            self.cb_issue_book.configure(values=["No available books"])
            self.cb_issue_book.set("No available books")

        # Update members combobox
        mems = [f"{m['id']} | {m['name']}" for m in self.db.get_members()]
        if mems:
            self.cb_issue_member.configure(values=mems)
            self.cb_issue_member.set(mems[0])
        else:
            self.cb_issue_member.configure(values=["No registered members"])
            self.cb_issue_member.set("No registered members")

        # Update return combobox
        active_issues = self.db.get_active_issues()
        ret_options = [f"{i['book_id']} | {i['book_title']} (Loaned to: {i['member_name']})" for i in active_issues]
        if ret_options:
            self.cb_return_book.configure(values=ret_options)
            self.cb_return_book.set(ret_options[0])
            self._on_return_selection_changed(ret_options[0])
        else:
            self.cb_return_book.configure(values=["No active checkouts"])
            self.cb_return_book.set("No active checkouts")
            self.lbl_return_info.configure(text="No active checkouts currently selected.", text_color=Theme.TEXT_SECONDARY)

        # Update Table
        for item in self.issue_tree.get_children():
            self.issue_tree.delete(item)

        today = date.today()
        if not active_issues:
            self.issue_tree.insert("", "end", values=("No books currently issued", "-", "-", "-", "-", "-", "All inventory available"), tags=("normal",))
            return

        for iss in active_issues:
            due_d = datetime.strptime(iss["due_date"], "%Y-%m-%d").date()
            days_diff = (due_d - today).days

            if days_diff < 0:
                status_text = f"OVERDUE by {abs(days_diff)}d (Fine: Rs. {abs(days_diff)*2})"
                tag = "overdue"
            elif days_diff == 0:
                status_text = "Due Today"
                tag = "overdue"
            else:
                status_text = f"{days_diff} days left"
                tag = "normal"

            self.issue_tree.insert("", "end", values=(
                iss["book_id"],
                iss["book_title"],
                iss["member_id"],
                iss["member_name"],
                iss["issue_date"],
                iss["due_date"],
                status_text
            ), tags=(tag,))

    def action_issue_book(self):
        b_sel = self.cb_issue_book.get().strip()
        m_sel = self.cb_issue_member.get().strip()

        if not b_sel or b_sel == "No available books" or not m_sel or m_sel == "No registered members":
            AlertModal.show_error(self.winfo_toplevel(), "Selection Error", "Please select a valid available book and member.")
            return

        book_id = b_sel.split("|")[0].strip()
        member_id = m_sel.split("|")[0].strip()

        today = date.today()
        due = today + timedelta(days=14)

        ok, msg = self.db.issue_book(book_id, member_id, today.strftime("%Y-%m-%d"), due.strftime("%Y-%m-%d"))
        if ok:
            AlertModal.show_success(self.winfo_toplevel(), "Checkout Successful", msg)
            self.refresh_data()
            self.app.set_status(f"Issued book {book_id} to member {member_id}")
        else:
            AlertModal.show_error(self.winfo_toplevel(), "Action Denied", msg)

    def action_return_book(self):
        ret_sel = self.cb_return_book.get().strip()
        if not ret_sel or ret_sel == "No active checkouts":
            AlertModal.show_warning(self.winfo_toplevel(), "Selection Required", "Please select a currently checked-out book to return.")
            return

        book_id = ret_sel.split("|")[0].strip()

        confirmed = ConfirmModal.ask(
            self.winfo_toplevel(),
            title="Confirm Return Check-In",
            message=f"Are you sure you want to process check-in for Book ID: '{book_id}'?",
            confirm_text="Confirm Return"
        )

        if not confirmed:
            return

        ok, fine, msg = self.db.return_book(book_id)
        if ok:
            if fine > 0:
                AlertModal.show_warning(self.winfo_toplevel(), "Returned with Late Fine", msg)
            else:
                AlertModal.show_success(self.winfo_toplevel(), "Return Completed", msg)
            self.refresh_data()
            self.app.set_status(f"Returned book {book_id} | Assessed Fine: Rs. {fine}")
        else:
            AlertModal.show_error(self.winfo_toplevel(), "Error", msg)

    def sort_column(self, col):
        current_dir = self.sort_directions.get(col, False)
        reverse = not current_dir
        self.sort_directions[col] = reverse

        items = [(self.issue_tree.set(k, col), k) for k in self.issue_tree.get_children("")]
        items.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (val, k) in enumerate(items):
            self.issue_tree.move(k, "", index)

        for c in self.issue_tree["columns"]:
            heading_txt = c
            if c == col:
                heading_txt += " ▲" if not reverse else " ▼"
            self.issue_tree.heading(c, text=heading_txt)
