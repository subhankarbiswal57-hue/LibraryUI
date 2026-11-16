"""
Books View: Modern SaaS Book Inventory Management
Features:
- Dual View modes: Modern Responsive Data Table & Visual Card Grid
- Instant live search & Category dropdown filter
- Clean side Add/Quick-Action drawer
- Double-click edit modal & validation-enforced deletion
- Empty states & badge pills
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from ui_theme import Theme
from ui_dialogs import ConfirmModal, AlertModal, ModernDialog

class BooksView(ctk.CTkFrame):
    def __init__(self, parent, db, app_instance, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self.app = app_instance
        self.current_view_mode = "table" # "table" or "grid"
        self.sort_directions = {}

        self._build_ui()

    def _build_ui(self):
        # 1. Header with Title, Stats count, View Switcher & Actions
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 14))

        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.pack(side="left")

        self.lbl_title = ctk.CTkLabel(
            title_box,
            text="Book Inventory",
            font=(Theme.FONT_FAMILY, 24, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            title_box,
            text="Catalog, search, and manage books in your collection",
            font=(Theme.FONT_FAMILY, 12),
            text_color=Theme.TEXT_SECONDARY
        )
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

        # View Switcher (Table / Cards)
        view_toggle_frame = ctk.CTkFrame(top_bar, fg_color=Theme.SURFACE_MUTED, corner_radius=8, height=36)
        view_toggle_frame.pack(side="right")

        self.btn_view_table = ctk.CTkButton(
            view_toggle_frame,
            text="📋 Table",
            width=80,
            height=30,
            corner_radius=6,
            font=(Theme.FONT_FAMILY, 11, "bold"),
            fg_color=Theme.BG_CARD,
            text_color=Theme.PRIMARY,
            hover_color=Theme.BORDER_LIGHT,
            command=lambda: self.switch_view("table")
        )
        self.btn_view_table.pack(side="left", padx=3, pady=3)

        self.btn_view_grid = ctk.CTkButton(
            view_toggle_frame,
            text="⊞ Grid",
            width=80,
            height=30,
            corner_radius=6,
            font=(Theme.FONT_FAMILY, 11, "bold"),
            fg_color="transparent",
            text_color=Theme.TEXT_SECONDARY,
            hover_color=Theme.BORDER_LIGHT,
            command=lambda: self.switch_view("grid")
        )
        self.btn_view_grid.pack(side="left", padx=3, pady=3)

        # 2. Controls Toolbar: Search, Category Filter, and Status Filter
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

        # Search Entry
        search_icon = ctk.CTkLabel(tb_inner, text="🔍", font=(Theme.FONT_FAMILY, 12))
        search_icon.pack(side="left", padx=(0, 6))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_content())
        self.search_entry = ctk.CTkEntry(
            tb_inner,
            textvariable=self.search_var,
            placeholder_text="Search by title, author, ID or genre...",
            font=(Theme.FONT_FAMILY, 12),
            width=280,
            height=32,
            fg_color=Theme.SURFACE_MUTED,
            border_color=Theme.BORDER_LIGHT,
            corner_radius=6
        )
        self.search_entry.pack(side="left", padx=(0, 14))

        # Category Filter
        lbl_cat = ctk.CTkLabel(tb_inner, text="Category:", font=(Theme.FONT_FAMILY, 12, "bold"), text_color=Theme.TEXT_SECONDARY)
        lbl_cat.pack(side="left", padx=(0, 6))

        self.cat_filter_var = ctk.StringVar(value="All Categories")
        categories = ["All Categories", "Fiction", "Non-Fiction", "Tech", "Science", "History", "Education", "Biography"]
        self.cat_menu = ctk.CTkOptionMenu(
            tb_inner,
            variable=self.cat_filter_var,
            values=categories,
            width=140,
            height=32,
            font=(Theme.FONT_FAMILY, 11),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            button_color=Theme.BORDER_LIGHT,
            button_hover_color=Theme.BORDER_SUBTLE,
            corner_radius=6,
            command=lambda v: self.refresh_content()
        )
        self.cat_menu.pack(side="left", padx=(0, 14))

        # Status Filter
        lbl_stat = ctk.CTkLabel(tb_inner, text="Status:", font=(Theme.FONT_FAMILY, 12, "bold"), text_color=Theme.TEXT_SECONDARY)
        lbl_stat.pack(side="left", padx=(0, 6))

        self.status_filter_var = ctk.StringVar(value="All Status")
        self.stat_menu = ctk.CTkOptionMenu(
            tb_inner,
            variable=self.status_filter_var,
            values=["All Status", "Available", "Issued"],
            width=120,
            height=32,
            font=(Theme.FONT_FAMILY, 11),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            button_color=Theme.BORDER_LIGHT,
            button_hover_color=Theme.BORDER_SUBTLE,
            corner_radius=6,
            command=lambda v: self.refresh_content()
        )
        self.stat_menu.pack(side="left")

        # 3. Main Split Container (Left: Content Table/Grid, Right: Modern Add Panel)
        main_split = ctk.CTkFrame(self, fg_color="transparent")
        main_split.pack(fill="both", expand=True)

        # Left Display Container
        self.display_container = ctk.CTkFrame(
            main_split,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        self.display_container.pack(side="left", fill="both", expand=True, padx=(0, 14))

        # Right Side Action & Add Book Form Drawer
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

        # Initialize table view
        self._init_table_view()
        self.refresh_content()

    def _build_add_form(self, container):
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=18)

        f_title = ctk.CTkLabel(
            inner,
            text="➕ Add New Book",
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        f_title.pack(fill="x", pady=(0, 4))

        f_sub = ctk.CTkLabel(
            inner,
            text="Register a new accession into library inventory",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.TEXT_MUTED,
            anchor="w",
            wraplength=260
        )
        f_sub.pack(fill="x", pady=(0, 14))

        # Field: Book ID
        ctk.CTkLabel(inner, text="Book ID *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_id = ctk.CTkEntry(inner, placeholder_text="e.g. B106", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6, border_color=Theme.BORDER_LIGHT)
        self.ent_id.pack(fill="x", pady=(3, 10))

        # Field: Title
        ctk.CTkLabel(inner, text="Book Title *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_title = ctk.CTkEntry(inner, placeholder_text="e.g. Design Patterns", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6, border_color=Theme.BORDER_LIGHT)
        self.ent_title.pack(fill="x", pady=(3, 10))

        # Field: Author
        ctk.CTkLabel(inner, text="Author Name *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_author = ctk.CTkEntry(inner, placeholder_text="e.g. Erich Gamma", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6, border_color=Theme.BORDER_LIGHT)
        self.ent_author.pack(fill="x", pady=(3, 10))

        # Field: Category
        ctk.CTkLabel(inner, text="Category / Genre *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.cat_var = ctk.StringVar(value="Tech")
        self.cat_select = ctk.CTkOptionMenu(
            inner,
            variable=self.cat_var,
            values=["Tech", "Fiction", "Non-Fiction", "Science", "History", "Education", "Biography"],
            height=32,
            font=(Theme.FONT_FAMILY, 12),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            button_color=Theme.BORDER_LIGHT,
            button_hover_color=Theme.BORDER_SUBTLE,
            corner_radius=6
        )
        self.cat_select.pack(fill="x", pady=(3, 16))

        # Action Buttons
        btn_add = ctk.CTkButton(
            inner,
            text="Save to Inventory",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=self.action_add_book
        )
        btn_add.pack(fill="x", pady=(0, 8))

        btn_edit = ctk.CTkButton(
            inner,
            text="✏️ Edit Selected",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            hover_color=Theme.BORDER_LIGHT,
            corner_radius=8,
            height=34,
            command=self.open_edit_selected
        )
        btn_edit.pack(fill="x", pady=(0, 8))

        btn_delete = ctk.CTkButton(
            inner,
            text="🗑️ Delete Selected",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.DANGER_LIGHT,
            text_color=Theme.DANGER,
            hover_color=Theme.OVERDUE_BG,
            corner_radius=8,
            height=34,
            command=self.action_delete_selected
        )
        btn_delete.pack(fill="x", pady=(0, 10))

        hint_box = ctk.CTkFrame(inner, fg_color=Theme.PRIMARY_LIGHT, corner_radius=8)
        hint_box.pack(fill="x", side="bottom", pady=6)
        hint = ctk.CTkLabel(
            hint_box,
            text="💡 Tip: Double-click any row to edit book details or click headers to sort.",
            font=(Theme.FONT_FAMILY, 10),
            text_color=Theme.PRIMARY,
            wraplength=240,
            justify="left"
        )
        hint.pack(padx=10, pady=8)

    def _init_table_view(self):
        # Clear container
        for w in self.display_container.winfo_children():
            w.destroy()

        t_header = ctk.CTkFrame(self.display_container, fg_color="transparent")
        t_header.pack(fill="x", padx=14, pady=(12, 6))

        self.t_count_lbl = ctk.CTkLabel(
            t_header,
            text="Showing all books",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        self.t_count_lbl.pack(side="left")

        tree_wrapper = tk.Frame(self.display_container, bg="#FFFFFF")
        tree_wrapper.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        cols = ("ID", "Title", "Author", "Category", "Status")
        self.tree = ttk.Treeview(tree_wrapper, columns=cols, show="headings", style="Modern.Treeview")

        for c in cols:
            self.tree.heading(c, text=c, command=lambda _c=c: self.sort_column(_c))
            self.tree.column(c, anchor="w", width=120)

        self.tree.column("ID", width=75, anchor="center")
        self.tree.column("Title", width=220)
        self.tree.column("Author", width=160)
        self.tree.column("Category", width=110, anchor="center")
        self.tree.column("Status", width=95, anchor="center")

        sb = ttk.Scrollbar(tree_wrapper, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.tag_configure("Available", foreground=Theme.SUCCESS_TEXT)
        self.tree.tag_configure("Issued", foreground=Theme.WARNING_TEXT)

        self.tree.bind("<Double-1>", lambda e: self.open_edit_selected())

    def switch_view(self, mode):
        self.current_view_mode = mode
        if mode == "table":
            self.btn_view_table.configure(fg_color=Theme.BG_CARD, text_color=Theme.PRIMARY)
            self.btn_view_grid.configure(fg_color="transparent", text_color=Theme.TEXT_SECONDARY)
            self._init_table_view()
        else:
            self.btn_view_grid.configure(fg_color=Theme.BG_CARD, text_color=Theme.PRIMARY)
            self.btn_view_table.configure(fg_color="transparent", text_color=Theme.TEXT_SECONDARY)
            self._init_grid_view()
        self.refresh_content()

    def _init_grid_view(self):
        for w in self.display_container.winfo_children():
            w.destroy()

        t_header = ctk.CTkFrame(self.display_container, fg_color="transparent")
        t_header.pack(fill="x", padx=14, pady=(12, 6))

        self.t_count_lbl = ctk.CTkLabel(
            t_header,
            text="Showing book cards",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        self.t_count_lbl.pack(side="left")

        # Scrollable container for cards
        self.grid_scroll = ctk.CTkScrollableFrame(
            self.display_container,
            fg_color="transparent"
        )
        self.grid_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _get_filtered_books(self):
        q = self.search_var.get().strip().lower()
        selected_cat = self.cat_filter_var.get()
        selected_stat = self.status_filter_var.get()

        filtered = []
        for b in self.db.get_books():
            match_q = (
                q in b["id"].lower() or
                q in b["title"].lower() or
                q in b["author"].lower() or
                q in b["category"].lower() or
                q in b.get("status", "").lower()
            )
            match_cat = (selected_cat == "All Categories" or b["category"].lower() == selected_cat.lower())
            match_stat = (selected_stat == "All Status" or b.get("status", "").lower() == selected_stat.lower())

            if match_q and match_cat and match_stat:
                filtered.append(b)
        return filtered

    def refresh_content(self):
        books = self._get_filtered_books()
        total_all = len(self.db.get_books())
        self.t_count_lbl.configure(text=f"Showing {len(books)} of {total_all} registered titles")

        if self.current_view_mode == "table":
            for item in self.tree.get_children():
                self.tree.delete(item)

            if not books:
                self.tree.insert("", "end", values=("No books found matching search filters", "-", "-", "-", "-"))
                return

            for b in books:
                status = b.get("status", "Available")
                self.tree.insert("", "end", values=(
                    b["id"],
                    b["title"],
                    b["author"],
                    b["category"],
                    status
                ), tags=(status,))
        else:
            for w in self.grid_scroll.winfo_children():
                w.destroy()

            if not books:
                empty_lbl = ctk.CTkLabel(
                    self.grid_scroll,
                    text="🔍 No books match your search or filter criteria.",
                    font=(Theme.FONT_FAMILY, 14),
                    text_color=Theme.TEXT_MUTED
                )
                empty_lbl.pack(pady=40)
                return

            # Render responsive grid (2 columns)
            cols = 2
            for idx, b in enumerate(books):
                r = idx // cols
                c = idx % cols

                card = ctk.CTkFrame(
                    self.grid_scroll,
                    fg_color=Theme.SURFACE_MUTED,
                    corner_radius=10,
                    border_width=1,
                    border_color=Theme.BORDER_LIGHT
                )
                card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
                self.grid_scroll.grid_columnconfigure(c, weight=1)

                inner = ctk.CTkFrame(card, fg_color="transparent")
                inner.pack(fill="both", expand=True, padx=12, pady=12)

                top_r = ctk.CTkFrame(inner, fg_color="transparent")
                top_r.pack(fill="x")

                id_badge = ctk.CTkLabel(
                    top_r,
                    text=b["id"],
                    font=(Theme.FONT_FAMILY, 10, "bold"),
                    fg_color=Theme.PRIMARY_LIGHT,
                    text_color=Theme.PRIMARY,
                    corner_radius=4,
                    padx=6,
                    pady=2
                )
                id_badge.pack(side="left")

                is_avail = b.get("status") == "Available"
                stat_badge = ctk.CTkLabel(
                    top_r,
                    text="● Available" if is_avail else "● Issued",
                    font=(Theme.FONT_FAMILY, 10, "bold"),
                    fg_color=Theme.SUCCESS_LIGHT if is_avail else Theme.WARNING_LIGHT,
                    text_color=Theme.SUCCESS_TEXT if is_avail else Theme.WARNING_TEXT,
                    corner_radius=4,
                    padx=6,
                    pady=2
                )
                stat_badge.pack(side="right")

                title_lbl = ctk.CTkLabel(
                    inner,
                    text=b["title"],
                    font=(Theme.FONT_FAMILY, 13, "bold"),
                    text_color=Theme.TEXT_PRIMARY,
                    anchor="w",
                    wraplength=220
                )
                title_lbl.pack(fill="x", pady=(6, 2))

                author_lbl = ctk.CTkLabel(
                    inner,
                    text=f"by {b['author']}",
                    font=(Theme.FONT_FAMILY, 11),
                    text_color=Theme.TEXT_SECONDARY,
                    anchor="w"
                )
                author_lbl.pack(fill="x")

                bottom_r = ctk.CTkFrame(inner, fg_color="transparent")
                bottom_r.pack(fill="x", pady=(8, 0))

                cat_lbl = ctk.CTkLabel(
                    bottom_r,
                    text=f"📁 {b['category']}",
                    font=(Theme.FONT_FAMILY, 10),
                    text_color=Theme.TEXT_MUTED
                )
                cat_lbl.pack(side="left")

                btn_c_edit = ctk.CTkButton(
                    bottom_r,
                    text="Edit",
                    width=54,
                    height=24,
                    font=(Theme.FONT_FAMILY, 10, "bold"),
                    fg_color=Theme.BG_CARD,
                    text_color=Theme.TEXT_PRIMARY,
                    hover_color=Theme.BORDER_LIGHT,
                    corner_radius=4,
                    command=lambda book_obj=b: self.open_edit_dialog_direct(book_obj)
                )
                btn_c_edit.pack(side="right")

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

    def action_add_book(self):
        b_id = self.ent_id.get().strip()
        title = self.ent_title.get().strip()
        author = self.ent_author.get().strip()
        cat = self.cat_var.get().strip()

        if not b_id or not title or not author or not cat:
            AlertModal.show_error(self.winfo_toplevel(), "Validation Error", "All fields are required! Please provide Book ID, Title, Author, and Category.")
            return

        ok, msg = self.db.add_book(b_id, title, author, cat)
        if ok:
            AlertModal.show_success(self.winfo_toplevel(), "Book Registered", msg)
            self.ent_id.delete(0, "end")
            self.ent_title.delete(0, "end")
            self.ent_author.delete(0, "end")
            self.refresh_content()
            self.app.set_status(f"Added book: '{title}' ({b_id})")
        else:
            AlertModal.show_error(self.winfo_toplevel(), "Action Denied", msg)

    def open_edit_selected(self):
        if self.current_view_mode != "table":
            return
        sel = self.tree.selection()
        if not sel:
            AlertModal.show_warning(self.winfo_toplevel(), "Selection Required", "Please select a book from the table to edit.")
            return

        item = self.tree.item(sel[0])
        val = item["values"]
        if not val or val[0] == "No books found matching search filters":
            return

        book_id = str(val[0])
        book = next((b for b in self.db.get_books() if b["id"] == book_id), None)
        if book:
            self.open_edit_dialog_direct(book)

    def open_edit_dialog_direct(self, book):
        dlg = ModernDialog(self.winfo_toplevel(), title=f"Edit Book - {book['id']}", width=400, height=360)

        inner = ctk.CTkFrame(dlg, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            inner,
            text=f"Update Book details (ID: {book['id']})",
            font=(Theme.FONT_FAMILY, 16, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(inner, text="Title *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        t_ent = ctk.CTkEntry(inner, font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6)
        t_ent.pack(fill="x", pady=(3, 10))
        t_ent.insert(0, book["title"])

        ctk.CTkLabel(inner, text="Author *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        a_ent = ctk.CTkEntry(inner, font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6)
        a_ent.pack(fill="x", pady=(3, 10))
        a_ent.insert(0, book["author"])

        ctk.CTkLabel(inner, text="Category *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        c_var = ctk.StringVar(value=book.get("category", "Tech"))
        c_menu = ctk.CTkOptionMenu(
            inner,
            variable=c_var,
            values=["Fiction", "Non-Fiction", "Tech", "Science", "History", "Education", "Biography"],
            height=32,
            font=(Theme.FONT_FAMILY, 12),
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            button_color=Theme.BORDER_LIGHT,
            corner_radius=6
        )
        c_menu.pack(fill="x", pady=(3, 18))

        def save_changes():
            nt = t_ent.get().strip()
            na = a_ent.get().strip()
            nc = c_var.get().strip()

            ok, msg = self.db.update_book(book["id"], nt, na, nc)
            if ok:
                AlertModal.show_success(dlg, "Updated", msg)
                dlg.destroy()
                self.refresh_content()
                self.app.set_status(f"Updated book details for {book['id']}")
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

    def action_delete_selected(self):
        if self.current_view_mode != "table":
            AlertModal.show_warning(self.winfo_toplevel(), "Switch to Table", "Please switch to Table view to select and delete items.")
            return

        sel = self.tree.selection()
        if not sel:
            AlertModal.show_warning(self.winfo_toplevel(), "Selection Required", "Please select a book from the table to delete.")
            return

        val = self.tree.item(sel[0])["values"]
        if not val or val[0] == "No books found matching search filters":
            return

        book_id = str(val[0])
        title = str(val[1])

        confirmed = ConfirmModal.ask(
            self.winfo_toplevel(),
            title="Delete Book Confirmation",
            message=f"Are you sure you want to permanently delete:\n\n'{title}' (ID: {book_id})?\n\nThis action cannot be undone.",
            confirm_text="Delete Book",
            is_danger=True
        )

        if not confirmed:
            return

        ok, msg = self.db.delete_book(book_id)
        if ok:
            AlertModal.show_success(self.winfo_toplevel(), "Book Deleted", msg)
            self.refresh_content()
            self.app.set_status(f"Deleted book {book_id}")
        else:
            AlertModal.show_error(self.winfo_toplevel(), "Deletion Blocked", msg)
