"""
Members View: Modern SaaS Patron Management
Features:
- Dual View modes: Table View & SaaS Member Profile Cards
- Real-time search across ID, Name, Email, and Phone
- Dedicated Member Borrowing History & Active Loans Dialog
- Double-click edit modal & validated registration form
- Visual avatar initials & contact badges
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from ui_theme import Theme
from ui_dialogs import ConfirmModal, AlertModal, ModernDialog

class MembersView(ctk.CTkFrame):
    def __init__(self, parent, db, app_instance, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self.app = app_instance
        self.current_view_mode = "cards" # "cards" or "table"
        self.sort_directions = {}

        self._build_ui()

    def _build_ui(self):
        # 1. Top Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 14))

        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.pack(side="left")

        lbl_title = ctk.CTkLabel(
            title_box,
            text="Member Directory",
            font=(Theme.FONT_FAMILY, 24, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        lbl_title.pack(anchor="w")

        lbl_subtitle = ctk.CTkLabel(
            title_box,
            text="Manage library patrons, view loan activity, and borrowing history",
            font=(Theme.FONT_FAMILY, 12),
            text_color=Theme.TEXT_SECONDARY
        )
        lbl_subtitle.pack(anchor="w", pady=(2, 0))

        # View Switcher (Cards / Table)
        view_toggle_frame = ctk.CTkFrame(top_bar, fg_color=Theme.SURFACE_MUTED, corner_radius=8, height=36)
        view_toggle_frame.pack(side="right")

        self.btn_view_cards = ctk.CTkButton(
            view_toggle_frame,
            text="👤 Profile Cards",
            width=110,
            height=30,
            corner_radius=6,
            font=(Theme.FONT_FAMILY, 11, "bold"),
            fg_color=Theme.BG_CARD,
            text_color=Theme.PRIMARY,
            hover_color=Theme.BORDER_LIGHT,
            command=lambda: self.switch_view("cards")
        )
        self.btn_view_cards.pack(side="left", padx=3, pady=3)

        self.btn_view_table = ctk.CTkButton(
            view_toggle_frame,
            text="📋 Table",
            width=80,
            height=30,
            corner_radius=6,
            font=(Theme.FONT_FAMILY, 11, "bold"),
            fg_color="transparent",
            text_color=Theme.TEXT_SECONDARY,
            hover_color=Theme.BORDER_LIGHT,
            command=lambda: self.switch_view("table")
        )
        self.btn_view_table.pack(side="left", padx=3, pady=3)

        # 2. Controls Toolbar
        toolbar = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            height=52
        )
        toolbar.pack(fill="x", pady=(0, 14))

        tb_inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        tb_inner.pack(fill="both", expand=True, padx=14, pady=10)

        search_icon = ctk.CTkLabel(tb_inner, text="🔍", font=(Theme.FONT_FAMILY, 12))
        search_icon.pack(side="left", padx=(0, 6))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_content())
        self.search_entry = ctk.CTkEntry(
            tb_inner,
            textvariable=self.search_var,
            placeholder_text="Search members by name, ID, email, or phone...",
            font=(Theme.FONT_FAMILY, 12),
            width=360,
            height=32,
            fg_color=Theme.SURFACE_MUTED,
            border_color=Theme.BORDER_LIGHT,
            corner_radius=6
        )
        self.search_entry.pack(side="left")

        # 3. Main Split (Left: Cards/Table Container, Right: Add Member Panel)
        main_split = ctk.CTkFrame(self, fg_color="transparent")
        main_split.pack(fill="both", expand=True)

        self.display_container = ctk.CTkFrame(
            main_split,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        self.display_container.pack(side="left", fill="both", expand=True, padx=(0, 14))

        form_panel = ctk.CTkFrame(
            main_split,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            width=300
        )
        form_panel.pack(side="right", fill="y")
        form_panel.pack_propagate(False)

        self._build_add_form(form_panel)

        self.switch_view("cards")

    def _build_add_form(self, container):
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=18)

        f_title = ctk.CTkLabel(
            inner,
            text="➕ Register Member",
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        f_title.pack(fill="x", pady=(0, 4))

        f_sub = ctk.CTkLabel(
            inner,
            text="Enroll a new student or faculty member",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        )
        f_sub.pack(fill="x", pady=(0, 14))

        # Fields
        ctk.CTkLabel(inner, text="Member ID *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_mid = ctk.CTkEntry(inner, placeholder_text="e.g. M004", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6, border_color=Theme.BORDER_LIGHT)
        self.ent_mid.pack(fill="x", pady=(3, 10))

        ctk.CTkLabel(inner, text="Full Name *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_name = ctk.CTkEntry(inner, placeholder_text="e.g. Sarah Jenkins", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6, border_color=Theme.BORDER_LIGHT)
        self.ent_name.pack(fill="x", pady=(3, 10))

        ctk.CTkLabel(inner, text="Email Address *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_email = ctk.CTkEntry(inner, placeholder_text="e.g. sarah@example.com", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6, border_color=Theme.BORDER_LIGHT)
        self.ent_email.pack(fill="x", pady=(3, 10))

        ctk.CTkLabel(inner, text="Phone Number *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_phone = ctk.CTkEntry(inner, placeholder_text="e.g. 9876543210", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6, border_color=Theme.BORDER_LIGHT)
        self.ent_phone.pack(fill="x", pady=(3, 18))

        btn_add = ctk.CTkButton(
            inner,
            text="Enroll Member",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self.action_add_member
        )
        btn_add.pack(fill="x", pady=(0, 8))

        btn_hist = ctk.CTkButton(
            inner,
            text="📜 View Selected History",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            hover_color=Theme.BORDER_LIGHT,
            corner_radius=8,
            height=34,
            command=self.view_selected_history
        )
        btn_hist.pack(fill="x", pady=(0, 10))

        hint_box = ctk.CTkFrame(inner, fg_color=Theme.PRIMARY_LIGHT, corner_radius=8)
        hint_box.pack(fill="x", side="bottom", pady=6)
        hint = ctk.CTkLabel(
            hint_box,
            text="💡 Tip: Click 'History' on any profile card to view all current & past borrowed books.",
            font=(Theme.FONT_FAMILY, 10),
            text_color=Theme.PRIMARY,
            wraplength=240,
            justify="left"
        )
        hint.pack(padx=10, pady=8)

    def switch_view(self, mode):
        self.current_view_mode = mode
        if mode == "cards":
            self.btn_view_cards.configure(fg_color=Theme.BG_CARD, text_color=Theme.PRIMARY)
            self.btn_view_table.configure(fg_color="transparent", text_color=Theme.TEXT_SECONDARY)
            self._init_cards_view()
        else:
            self.btn_view_table.configure(fg_color=Theme.BG_CARD, text_color=Theme.PRIMARY)
            self.btn_view_cards.configure(fg_color="transparent", text_color=Theme.TEXT_SECONDARY)
            self._init_table_view()
        self.refresh_content()

    def _init_cards_view(self):
        for w in self.display_container.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self.display_container, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        self.count_lbl = ctk.CTkLabel(
            header,
            text="Showing member profiles",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        self.count_lbl.pack(side="left")

        self.cards_scroll = ctk.CTkScrollableFrame(
            self.display_container,
            fg_color="transparent"
        )
        self.cards_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _init_table_view(self):
        for w in self.display_container.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self.display_container, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        self.count_lbl = ctk.CTkLabel(
            header,
            text="Showing member table",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        self.count_lbl.pack(side="left")

        tree_wrapper = tk.Frame(self.display_container, bg="#FFFFFF")
        tree_wrapper.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        cols = ("Member ID", "Name", "Email", "Phone", "Active Loans")
        self.tree = ttk.Treeview(tree_wrapper, columns=cols, show="headings", style="Modern.Treeview")

        for c in cols:
            self.tree.heading(c, text=c, command=lambda _c=c: self.sort_column(_c))
            self.tree.column(c, anchor="w", width=120)

        self.tree.column("Member ID", width=80, anchor="center")
        self.tree.column("Name", width=180)
        self.tree.column("Email", width=200)
        self.tree.column("Phone", width=120)
        self.tree.column("Active Loans", width=95, anchor="center")

        sb = ttk.Scrollbar(tree_wrapper, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.open_edit_selected())

    def _get_filtered_members(self):
        q = self.search_var.get().strip().lower()
        filtered = []
        for m in self.db.get_members():
            if (
                q in m["id"].lower() or
                q in m["name"].lower() or
                q in m["email"].lower() or
                q in m["phone"].lower()
            ):
                filtered.append(m)
        return filtered

    def refresh_content(self):
        members = self._get_filtered_members()
        total_all = len(self.db.get_members())
        self.count_lbl.configure(text=f"Showing {len(members)} of {total_all} registered patrons")

        active_issues = self.db.get_active_issues()

        if self.current_view_mode == "table":
            for item in self.tree.get_children():
                self.tree.delete(item)

            if not members:
                self.tree.insert("", "end", values=("No members found", "-", "-", "-", "-"))
                return

            for m in members:
                loans_count = sum(1 for iss in active_issues if iss.get("member_id") == m["id"])
                self.tree.insert("", "end", values=(
                    m["id"],
                    m["name"],
                    m["email"],
                    m["phone"],
                    f"{loans_count} book(s)" if loans_count > 0 else "0"
                ))
        else:
            for w in self.cards_scroll.winfo_children():
                w.destroy()

            if not members:
                empty_lbl = ctk.CTkLabel(
                    self.cards_scroll,
                    text="🔍 No patrons match your search.",
                    font=(Theme.FONT_FAMILY, 14),
                    text_color=Theme.TEXT_MUTED
                )
                empty_lbl.pack(pady=40)
                return

            # Render 2-column card grid
            cols = 2
            for idx, m in enumerate(members):
                r = idx // cols
                c = idx % cols

                loans = [iss for iss in active_issues if iss.get("member_id") == m["id"]]
                loan_count = len(loans)

                card = ctk.CTkFrame(
                    self.cards_scroll,
                    fg_color=Theme.SURFACE_MUTED,
                    corner_radius=10,
                    border_width=1,
                    border_color=Theme.BORDER_LIGHT
                )
                card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
                self.cards_scroll.grid_columnconfigure(c, weight=1)

                inner = ctk.CTkFrame(card, fg_color="transparent")
                inner.pack(fill="both", expand=True, padx=14, pady=12)

                # Header with Avatar initials & ID
                top_row = ctk.CTkFrame(inner, fg_color="transparent")
                top_row.pack(fill="x")

                # Initials avatar
                initials = "".join([part[0].upper() for part in m["name"].split()[:2]]) if m["name"] else "M"
                avatar = ctk.CTkLabel(
                    top_row,
                    text=initials,
                    font=(Theme.FONT_FAMILY, 12, "bold"),
                    fg_color=Theme.PRIMARY,
                    text_color=Theme.TEXT_WHITE,
                    corner_radius=18,
                    width=36,
                    height=36
                )
                avatar.pack(side="left", padx=(0, 10))

                info_col = ctk.CTkFrame(top_row, fg_color="transparent")
                info_col.pack(side="left", fill="both", expand=True)

                name_lbl = ctk.CTkLabel(
                    info_col,
                    text=m["name"],
                    font=(Theme.FONT_FAMILY, 13, "bold"),
                    text_color=Theme.TEXT_PRIMARY,
                    anchor="w"
                )
                name_lbl.pack(anchor="w")

                id_lbl = ctk.CTkLabel(
                    info_col,
                    text=f"ID: {m['id']}",
                    font=(Theme.FONT_FAMILY, 10, "bold"),
                    text_color=Theme.TEXT_MUTED,
                    anchor="w"
                )
                id_lbl.pack(anchor="w")

                # Loan Badge
                loan_badge = ctk.CTkLabel(
                    top_row,
                    text=f"{loan_count} Active" if loan_count > 0 else "0 Loans",
                    font=(Theme.FONT_FAMILY, 10, "bold"),
                    fg_color=Theme.WARNING_LIGHT if loan_count > 0 else Theme.SUCCESS_LIGHT,
                    text_color=Theme.WARNING_TEXT if loan_count > 0 else Theme.SUCCESS_TEXT,
                    corner_radius=4,
                    padx=6,
                    pady=2
                )
                loan_badge.pack(side="right")

                # Contact info details
                details_box = ctk.CTkFrame(inner, fg_color="transparent")
                details_box.pack(fill="x", pady=(10, 8))

                email_lbl = ctk.CTkLabel(
                    details_box,
                    text=f"✉ {m['email']}",
                    font=(Theme.FONT_FAMILY, 11),
                    text_color=Theme.TEXT_SECONDARY,
                    anchor="w"
                )
                email_lbl.pack(fill="x")

                phone_lbl = ctk.CTkLabel(
                    details_box,
                    text=f"📞 {m['phone']}",
                    font=(Theme.FONT_FAMILY, 11),
                    text_color=Theme.TEXT_SECONDARY,
                    anchor="w"
                )
                phone_lbl.pack(fill="x")

                # Bottom actions row
                act_row = ctk.CTkFrame(inner, fg_color="transparent")
                act_row.pack(fill="x", pady=(6, 0))

                btn_hist = ctk.CTkButton(
                    act_row,
                    text="📜 History",
                    font=(Theme.FONT_FAMILY, 10, "bold"),
                    height=26,
                    fg_color=Theme.BG_CARD,
                    text_color=Theme.PRIMARY,
                    hover_color=Theme.BORDER_LIGHT,
                    corner_radius=5,
                    command=lambda mid=m['id'], mname=m['name']: self.show_history_dialog(mid, mname)
                )
                btn_hist.pack(side="left", padx=(0, 6))

                btn_edit = ctk.CTkButton(
                    act_row,
                    text="✏ Edit",
                    font=(Theme.FONT_FAMILY, 10, "bold"),
                    height=26,
                    fg_color=Theme.BG_CARD,
                    text_color=Theme.TEXT_PRIMARY,
                    hover_color=Theme.BORDER_LIGHT,
                    corner_radius=5,
                    command=lambda mem=m: self.open_edit_dialog_direct(mem)
                )
                btn_edit.pack(side="right")

    def sort_column(self, col):
        current_dir = self.sort_directions.get(col, False)
        reverse = not current_dir
        self.sort_directions[col] = reverse

        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        items.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

        for c in self.tree["columns"]:
            heading_txt = c
            if c == col:
                heading_txt += " ▲" if not reverse else " ▼"
            self.tree.heading(c, text=heading_txt)

    def action_add_member(self):
        mid = self.ent_mid.get().strip()
        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        phone = self.ent_phone.get().strip()

        if not mid or not name or not email or not phone:
            AlertModal.show_error(self.winfo_toplevel(), "Validation Error", "All fields are required! Please provide ID, Name, Email, and Phone.")
            return

        ok, msg = self.db.add_member(mid, name, email, phone)
        if ok:
            AlertModal.show_success(self.winfo_toplevel(), "Member Enrolled", msg)
            self.ent_mid.delete(0, "end")
            self.ent_name.delete(0, "end")
            self.ent_email.delete(0, "end")
            self.ent_phone.delete(0, "end")
            self.refresh_content()
            self.app.set_status(f"Registered member: '{name}' ({mid})")
        else:
            AlertModal.show_error(self.winfo_toplevel(), "Action Blocked", msg)

    def open_edit_selected(self):
        if self.current_view_mode != "table":
            return
        sel = self.tree.selection()
        if not sel:
            AlertModal.show_warning(self.winfo_toplevel(), "Selection Required", "Please select a member row to edit.")
            return

        val = self.tree.item(sel[0])["values"]
        if not val or val[0] == "No members found":
            return

        mid = str(val[0])
        mem = next((m for m in self.db.get_members() if m["id"] == mid), None)
        if mem:
            self.open_edit_dialog_direct(mem)

    def view_selected_history(self):
        if self.current_view_mode == "table":
            sel = self.tree.selection()
            if not sel:
                AlertModal.show_warning(self.winfo_toplevel(), "Selection Required", "Please select a member from the table to view history.")
                return
            val = self.tree.item(sel[0])["values"]
            if not val or val[0] == "No members found":
                return
            mid = str(val[0])
            name = str(val[1])
            self.show_history_dialog(mid, name)
        else:
            AlertModal.show_info(self.winfo_toplevel(), "View History", "Click the '📜 History' button directly on any member card.")

    def open_edit_dialog_direct(self, mem):
        dlg = ModernDialog(self.winfo_toplevel(), title=f"Edit Member - {mem['id']}", width=400, height=360)

        inner = ctk.CTkFrame(dlg, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            inner,
            text=f"Update Patron (ID: {mem['id']})",
            font=(Theme.FONT_FAMILY, 16, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(inner, text="Full Name *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        n_ent = ctk.CTkEntry(inner, font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6)
        n_ent.pack(fill="x", pady=(3, 10))
        n_ent.insert(0, mem["name"])

        ctk.CTkLabel(inner, text="Email *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        e_ent = ctk.CTkEntry(inner, font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6)
        e_ent.pack(fill="x", pady=(3, 10))
        e_ent.insert(0, mem["email"])

        ctk.CTkLabel(inner, text="Phone *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        p_ent = ctk.CTkEntry(inner, font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6)
        p_ent.pack(fill="x", pady=(3, 18))
        p_ent.insert(0, mem["phone"])

        def save_changes():
            nn = n_ent.get().strip()
            ne = e_ent.get().strip()
            np = p_ent.get().strip()

            ok, msg = self.db.update_member(mem["id"], nn, ne, np)
            if ok:
                AlertModal.show_success(dlg, "Updated", msg)
                dlg.destroy()
                self.refresh_content()
                self.app.set_status(f"Updated member details for {mem['id']}")
            else:
                AlertModal.show_error(dlg, "Error", msg)

        btn_save = ctk.CTkButton(
            inner,
            text="Save Changes",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=save_changes
        )
        btn_save.pack(fill="x", side="bottom")

    def show_history_dialog(self, member_id, member_name):
        dlg = ModernDialog(self.winfo_toplevel(), title=f"Borrowing History - {member_name}", width=760, height=440)

        inner = ctk.CTkFrame(dlg, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            header,
            text=f"Circulation Records for {member_name} ({member_id})",
            font=(Theme.FONT_FAMILY, 16, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left")

        history = self.db.get_member_history(member_id)

        tbl_f = tk.Frame(inner, bg="#FFFFFF")
        tbl_f.pack(fill="both", expand=True)

        cols = ("Book ID", "Title", "Issue Date", "Due Date", "Status", "Return Date", "Fine (Rs.)")
        tree = ttk.Treeview(tbl_f, columns=cols, show="headings", style="Modern.Treeview")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=95)
        tree.column("Title", anchor="w", width=180)

        sb = ttk.Scrollbar(tbl_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        if not history:
            tree.insert("", "end", values=("No circulation records found", "-", "-", "-", "-", "-", "-"))
        else:
            for h in history:
                tree.insert("", "end", values=(
                    h.get("book_id"),
                    h.get("book_title"),
                    h.get("issue_date"),
                    h.get("due_date"),
                    h.get("status"),
                    h.get("return_date", "-"),
                    h.get("fine", 0)
                ))
