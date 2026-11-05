"""
Library Management System (GUI using Tkinter)
Features:
- Authentication & Session management (Login, Change Password, Logout)
- Dashboard overview with live stats counters
- Books Management: Table, live search, add, edit (double click), delete validation
- Members Management: Table, live search, add, edit (double click), history view
- Issue & Return System: 14-day default due date, return processing, Rs 2/day late fine
- Visual Indicators: Red highlight for overdue records
- Extras: Dark / Light mode toggle, column header sorting, JSON persistence
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from database import Database

class ModernTheme:
    LIGHT = {
        "bg": "#f4f6f9",
        "card_bg": "#ffffff",
        "fg": "#212529",
        "accent": "#4361ee",
        "accent_hover": "#3a56d4",
        "sidebar_bg": "#1e293b",
        "sidebar_fg": "#f8fafc",
        "sidebar_active": "#334155",
        "border": "#e2e8f0",
        "danger": "#ef4444",
        "success": "#10b981",
        "warning": "#f59e0b",
        "tree_bg": "#ffffff",
        "tree_fg": "#1e293b",
        "tree_select": "#dbeafe",
        "tree_alt": "#f8fafc",
        "overdue_bg": "#fee2e2",
        "overdue_fg": "#991b1b"
    }

    DARK = {
        "bg": "#0f172a",
        "card_bg": "#1e293b",
        "fg": "#f8fafc",
        "accent": "#6366f1",
        "accent_hover": "#4f46e5",
        "sidebar_bg": "#0b0f19",
        "sidebar_fg": "#e2e8f0",
        "sidebar_active": "#1e293b",
        "border": "#334155",
        "danger": "#f87171",
        "success": "#34d399",
        "warning": "#fbbf24",
        "tree_bg": "#1e293b",
        "tree_fg": "#f1f5f9",
        "tree_select": "#312e81",
        "tree_alt": "#192231",
        "overdue_bg": "#7f1d1d",
        "overdue_fg": "#fecaca"
    }

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1100x700")
        self.root.minsize(980, 620)

        self.db = Database()
        self.current_user = None
        self.dark_mode = False
        self.theme = ModernTheme.LIGHT

        # Sort order trackers
        self.sort_directions = {}

        self.setup_styles()
        self.show_login_screen()

    def get_color(self, key):
        return self.theme.get(key, "#ffffff")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme = ModernTheme.DARK if self.dark_mode else ModernTheme.LIGHT
        self.setup_styles()
        if self.current_user:
            self.show_main_app()
        else:
            self.show_login_screen()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        bg = self.get_color("bg")
        fg = self.get_color("fg")
        card = self.get_color("card_bg")
        accent = self.get_color("accent")
        border = self.get_color("border")

        self.root.configure(bg=bg)

        # Style Treeview
        self.style.configure("Custom.Treeview",
                             background=self.get_color("tree_bg"),
                             foreground=self.get_color("tree_fg"),
                             fieldbackground=self.get_color("tree_bg"),
                             rowheight=28,
                             borderwidth=0,
                             font=("Segoe UI", 10))
        self.style.map("Custom.Treeview",
                       background=[("selected", self.get_color("tree_select"))],
                       foreground=[("selected", fg)])

        self.style.configure("Custom.Treeview.Heading",
                             background=card,
                             foreground=fg,
                             font=("Segoe UI", 10, "bold"),
                             padding=6,
                             relief="flat")
        self.style.map("Custom.Treeview.Heading",
                       background=[("active", self.get_color("border"))])

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------------- LOGIN SCREEN ----------------
    def show_login_screen(self):
        self.clear_root()
        bg = self.get_color("bg")
        card = self.get_color("card_bg")
        fg = self.get_color("fg")
        accent = self.get_color("accent")

        # Top toggle bar
        top_bar = tk.Frame(self.root, bg=bg)
        top_bar.pack(fill="x", padx=15, pady=10)
        theme_btn = tk.Button(top_bar, text="🌙 Dark Mode" if not self.dark_mode else "☀️ Light Mode",
                              bg=card, fg=fg, relief="flat", padx=10, pady=4, cursor="hand2",
                              font=("Segoe UI", 9, "bold"), command=self.toggle_theme)
        theme_btn.pack(side="right")

        # Container
        center_frame = tk.Frame(self.root, bg=bg)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        card_frame = tk.Frame(center_frame, bg=card, padx=40, pady=35,
                              highlightbackground=self.get_color("border"), highlightthickness=1)
        card_frame.pack()

        # Title
        title_lbl = tk.Label(card_frame, text="📚 Library System", font=("Segoe UI", 20, "bold"),
                             bg=card, fg=accent)
        title_lbl.pack(pady=(0, 5))

        subtitle_lbl = tk.Label(card_frame, text="Sign in to your account", font=("Segoe UI", 10),
                                bg=card, fg="#64748b")
        subtitle_lbl.pack(pady=(0, 25))

        # Username
        tk.Label(card_frame, text="Username", font=("Segoe UI", 10, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.login_user_ent = tk.Entry(card_frame, font=("Segoe UI", 11), width=28,
                                       relief="solid", bd=1, bg=bg, fg=fg)
        self.login_user_ent.pack(pady=(5, 15), ipady=4)
        self.login_user_ent.insert(0, "admin")

        # Password
        tk.Label(card_frame, text="Password", font=("Segoe UI", 10, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.login_pwd_ent = tk.Entry(card_frame, font=("Segoe UI", 11), width=28,
                                      show="•", relief="solid", bd=1, bg=bg, fg=fg)
        self.login_pwd_ent.pack(pady=(5, 20), ipady=4)
        self.login_pwd_ent.insert(0, "admin123")
        self.login_pwd_ent.bind("<Return>", lambda e: self.process_login())

        # Login button
        btn_login = tk.Button(card_frame, text="Login", font=("Segoe UI", 11, "bold"),
                              bg=accent, fg="#ffffff", activebackground=self.get_color("accent_hover"),
                              activeforeground="#ffffff", relief="flat", cursor="hand2",
                              command=self.process_login)
        btn_login.pack(fill="x", pady=(5, 10), ipady=4)

        hint_lbl = tk.Label(card_frame, text="Default: admin / admin123", font=("Segoe UI", 8),
                            bg=card, fg="#94a3b8")
        hint_lbl.pack()

    def process_login(self):
        u = self.login_user_ent.get().strip()
        p = self.login_pwd_ent.get()

        if not u or not p:
            messagebox.showerror("Login Error", "Please fill in both Username and Password fields.")
            return

        if self.db.verify_login(u, p):
            self.current_user = u
            self.show_main_app()
        else:
            messagebox.showerror("Access Denied", "Invalid username or password! Please try again.")

    # ---------------- MAIN APP LAYOUT ----------------
    def show_main_app(self):
        self.clear_root()
        bg = self.get_color("bg")
        fg = self.get_color("fg")

        # Setup Menu Bar
        self.create_menu_bar()

        # Layout: Sidebar on left, Content on right, Status bar at bottom
        self.status_var = tk.StringVar(value=f"Logged in as: {self.current_user} | Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 9),
                              bg=self.get_color("sidebar_bg"), fg=self.get_color("sidebar_fg"),
                              anchor="w", padx=10, pady=4)
        status_bar.pack(side="bottom", fill="x")

        main_container = tk.Frame(self.root, bg=bg)
        main_container.pack(side="top", fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main_container, bg=self.get_color("sidebar_bg"), width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Brand
        brand_lbl = tk.Label(sidebar, text="📚 LibraryUI", font=("Segoe UI", 15, "bold"),
                             bg=self.get_color("sidebar_bg"), fg="#38bdf8", pady=20)
        brand_lbl.pack(fill="x")

        # Nav Buttons
        nav_items = [
            ("📊 Dashboard", self.render_dashboard),
            ("📖 Books", self.render_books),
            ("👥 Members", self.render_members),
            ("🔄 Issue / Return", self.render_issue_return),
        ]

        self.nav_buttons = {}
        for text, cmd in nav_items:
            btn = tk.Button(sidebar, text=f"  {text}", font=("Segoe UI", 11),
                            bg=self.get_color("sidebar_bg"), fg=self.get_color("sidebar_fg"),
                            activebackground=self.get_color("sidebar_active"),
                            activeforeground="#ffffff", relief="flat", anchor="w",
                            padx=15, pady=10, cursor="hand2", command=cmd)
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_buttons[text] = btn

        # Bottom sidebar buttons (Theme, Logout)
        bot_sidebar = tk.Frame(sidebar, bg=self.get_color("sidebar_bg"))
        bot_sidebar.pack(side="bottom", fill="x", pady=15, padx=8)

        theme_lbl = "🌙 Dark Mode" if not self.dark_mode else "☀️ Light Mode"
        btn_theme = tk.Button(bot_sidebar, text=f"  {theme_lbl}", font=("Segoe UI", 10),
                              bg=self.get_color("sidebar_active"), fg=self.get_color("sidebar_fg"),
                              relief="flat", anchor="w", padx=10, pady=6, cursor="hand2",
                              command=self.toggle_theme)
        btn_theme.pack(fill="x", pady=3)

        btn_logout = tk.Button(bot_sidebar, text="  🚪 Logout", font=("Segoe UI", 10),
                               bg="#dc2626", fg="#ffffff", relief="flat", anchor="w",
                               padx=10, pady=6, cursor="hand2", command=self.action_logout)
        btn_logout.pack(fill="x", pady=3)

        # Content area
        self.content_frame = tk.Frame(main_container, bg=bg)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=15)

        # Default to Dashboard
        self.render_dashboard()

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Reload Data", command=self.reload_data)
        file_menu.add_separator()
        file_menu.add_command(label="Change Password", command=self.open_change_password_dialog)
        file_menu.add_command(label="Logout", command=self.action_logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Dashboard", command=self.render_dashboard)
        view_menu.add_command(label="Books", command=self.render_books)
        view_menu.add_command(label="Members", command=self.render_members)
        view_menu.add_command(label="Issue & Return", command=self.render_issue_return)
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def reload_data(self):
        self.db.load()
        self.set_status("Data reloaded from file successfully.")
        messagebox.showinfo("Data Reloaded", "Library data refreshed from disk.")
        self.render_dashboard()

    def show_about(self):
        messagebox.showinfo("About LibraryUI",
                            "Library Management System v1.0\nBuilt with Python & Tkinter\nComplete with live stats, search, validations, and overdue alerts.")

    def set_status(self, msg):
        self.status_var.set(f"User: {self.current_user} | {msg}")

    def action_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?"):
            self.current_user = None
            self.root.config(menu="")
            self.show_login_screen()

    def open_change_password_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Change Password")
        dlg.geometry("360x280")
        dlg.resizable(False, False)
        dlg.configure(bg=self.get_color("card_bg"))
        dlg.transient(self.root)
        dlg.grab_set()

        card = self.get_color("card_bg")
        fg = self.get_color("fg")

        tk.Label(dlg, text="Change Account Password", font=("Segoe UI", 12, "bold"),
                 bg=card, fg=self.get_color("accent")).pack(pady=12)

        f = tk.Frame(dlg, bg=card, padx=20)
        f.pack(fill="x")

        tk.Label(f, text="Current Password:", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        old_ent = tk.Entry(f, show="•", font=("Segoe UI", 10), bg=self.get_color("bg"), fg=fg)
        old_ent.pack(fill="x", pady=(2, 8))

        tk.Label(f, text="New Password:", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        new_ent = tk.Entry(f, show="•", font=("Segoe UI", 10), bg=self.get_color("bg"), fg=fg)
        new_ent.pack(fill="x", pady=(2, 8))

        tk.Label(f, text="Confirm New Password:", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        conf_ent = tk.Entry(f, show="•", font=("Segoe UI", 10), bg=self.get_color("bg"), fg=fg)
        conf_ent.pack(fill="x", pady=(2, 12))

        def save_pw():
            old_p = old_ent.get()
            new_p = new_ent.get()
            conf_p = conf_ent.get()

            if not old_p or not new_p or not conf_p:
                messagebox.showerror("Error", "All fields are required!", parent=dlg)
                return
            if new_p != conf_p:
                messagebox.showerror("Error", "New passwords do not match!", parent=dlg)
                return

            ok, msg = self.db.change_password(self.current_user, old_p, new_p)
            if ok:
                messagebox.showinfo("Success", msg, parent=dlg)
                dlg.destroy()
            else:
                messagebox.showerror("Error", msg, parent=dlg)

        btn = tk.Button(dlg, text="Update Password", font=("Segoe UI", 10, "bold"),
                        bg=self.get_color("accent"), fg="#ffffff", relief="flat",
                        command=save_pw, cursor="hand2")
        btn.pack(pady=5, ipadx=10, ipady=3)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ---------------- 1. DASHBOARD ----------------
    def render_dashboard(self):
        self.clear_content()
        self.set_status("Dashboard loaded")
        bg = self.get_color("bg")
        card = self.get_color("card_bg")
        fg = self.get_color("fg")

        # Header
        head_f = tk.Frame(self.content_frame, bg=bg)
        head_f.pack(fill="x", pady=(0, 20))
        tk.Label(head_f, text="Dashboard Overview", font=("Segoe UI", 18, "bold"),
                 bg=bg, fg=fg).pack(side="left")

        # Stats Cards
        stats = self.db.get_stats()
        cards_data = [
            ("📚 Total Books", stats["total_books"], "#3b82f6"),
            ("✅ Available Books", stats["available_books"], "#10b981"),
            ("⏳ Issued Books", stats["issued_books"], "#f59e0b"),
            ("👥 Total Members", stats["total_members"], "#8b5cf6"),
        ]

        cards_frame = tk.Frame(self.content_frame, bg=bg)
        cards_frame.pack(fill="x", pady=(0, 25))

        for idx, (title, val, color) in enumerate(cards_data):
            c = tk.Frame(cards_frame, bg=card, padx=15, pady=15,
                         highlightbackground=self.get_color("border"), highlightthickness=1)
            c.grid(row=0, column=idx, padx=8, sticky="nsew")
            cards_frame.grid_columnconfigure(idx, weight=1)

            tk.Label(c, text=title, font=("Segoe UI", 11, "bold"), bg=card, fg="#64748b").pack(anchor="w")
            tk.Label(c, text=str(val), font=("Segoe UI", 26, "bold"), bg=card, fg=color).pack(anchor="w", pady=(8, 0))

        # Recent Issues & Overdue alert table in Dashboard
        sub_title = tk.Label(self.content_frame, text="Active Issued Books & Overdue Tracker",
                             font=("Segoe UI", 13, "bold"), bg=bg, fg=fg)
        sub_title.pack(anchor="w", pady=(0, 10))

        table_frame = tk.Frame(self.content_frame, bg=card,
                               highlightbackground=self.get_color("border"), highlightthickness=1)
        table_frame.pack(fill="both", expand=True)

        cols = ("Book ID", "Title", "Member ID", "Member Name", "Issue Date", "Due Date", "Days Remaining / Overdue")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Custom.Treeview")

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        tree.column("Title", anchor="w", width=180)
        tree.column("Member Name", anchor="w", width=150)

        # Scrollbar
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Color tags
        tree.tag_configure("overdue", background=self.get_color("overdue_bg"), foreground=self.get_color("overdue_fg"))

        today = date.today()
        issues = self.db.get_active_issues()
        if not issues:
            tree.insert("", "end", values=("No books currently issued", "-", "-", "-", "-", "-", "-"))
        else:
            for iss in issues:
                due_d = datetime.strptime(iss["due_date"], "%Y-%m-%d").date()
                days_diff = (due_d - today).days
                if days_diff < 0:
                    status_text = f"OVERDUE by {abs(days_diff)} days (Fine: Rs. {abs(days_diff)*2})"
                    tag = "overdue"
                else:
                    status_text = f"{days_diff} days remaining"
                    tag = ""

                tree.insert("", "end", values=(
                    iss["book_id"], iss["book_title"], iss["member_id"], iss["member_name"],
                    iss["issue_date"], iss["due_date"], status_text
                ), tags=(tag,) if tag else ())

    # ---------------- 2. BOOKS MANAGEMENT ----------------
    def render_books(self):
        self.clear_content()
        self.set_status("Books management")
        bg = self.get_color("bg")
        card = self.get_color("card_bg")
        fg = self.get_color("fg")

        # Top Bar: Title & Live Search
        top_bar = tk.Frame(self.content_frame, bg=bg)
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(top_bar, text="Book Inventory", font=("Segoe UI", 16, "bold"),
                 bg=bg, fg=fg).pack(side="left")

        # Live Search Box
        search_f = tk.Frame(top_bar, bg=bg)
        search_f.pack(side="right")
        tk.Label(search_f, text="🔍 Search:", font=("Segoe UI", 10, "bold"), bg=bg, fg=fg).pack(side="left", padx=5)
        self.book_search_var = tk.StringVar()
        self.book_search_var.trace_add("write", lambda *args: self.refresh_books_table())
        search_ent = tk.Entry(search_f, textvariable=self.book_search_var, font=("Segoe UI", 10),
                              width=22, relief="solid", bd=1, bg=card, fg=fg)
        search_ent.pack(side="left", ipady=2)

        # Main Split: Left is Table, Right is Add Form
        split_f = tk.Frame(self.content_frame, bg=bg)
        split_f.pack(fill="both", expand=True)

        # Table Container
        tbl_container = tk.Frame(split_f, bg=card, highlightbackground=self.get_color("border"), highlightthickness=1)
        tbl_container.pack(side="left", fill="both", expand=True, padx=(0, 12))

        cols = ("ID", "Title", "Author", "Category", "Status")
        self.book_tree = ttk.Treeview(tbl_container, columns=cols, show="headings", style="Custom.Treeview")

        for c in cols:
            self.book_tree.heading(c, text=c, command=lambda _c=c: self.sort_tree(self.book_tree, _c))
            self.book_tree.column(c, anchor="w", width=110)
        self.book_tree.column("ID", width=70, anchor="center")
        self.book_tree.column("Title", width=180)
        self.book_tree.column("Status", width=90, anchor="center")

        sb = ttk.Scrollbar(tbl_container, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=sb.set)
        self.book_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Double click to edit
        self.book_tree.bind("<Double-1>", lambda e: self.open_edit_book_dialog())

        # Form Container (Add Book)
        form_frame = tk.Frame(split_f, bg=card, width=300, padx=18, pady=15,
                              highlightbackground=self.get_color("border"), highlightthickness=1)
        form_frame.pack(side="right", fill="y")
        form_frame.pack_propagate(False)

        tk.Label(form_frame, text="Add New Book", font=("Segoe UI", 13, "bold"),
                 bg=card, fg=self.get_color("accent")).pack(anchor="w", pady=(0, 12))

        # Fields
        tk.Label(form_frame, text="Book ID *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.b_id_ent = tk.Entry(form_frame, font=("Segoe UI", 10), bg=bg, fg=fg, relief="solid", bd=1)
        self.b_id_ent.pack(fill="x", pady=(2, 8), ipady=2)

        tk.Label(form_frame, text="Title *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.b_title_ent = tk.Entry(form_frame, font=("Segoe UI", 10), bg=bg, fg=fg, relief="solid", bd=1)
        self.b_title_ent.pack(fill="x", pady=(2, 8), ipady=2)

        tk.Label(form_frame, text="Author *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.b_author_ent = tk.Entry(form_frame, font=("Segoe UI", 10), bg=bg, fg=fg, relief="solid", bd=1)
        self.b_author_ent.pack(fill="x", pady=(2, 8), ipady=2)

        tk.Label(form_frame, text="Category *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.b_cat_ent = ttk.Combobox(form_frame, font=("Segoe UI", 10),
                                      values=["Fiction", "Non-Fiction", "Tech", "Science", "History", "Education", "Biography"])
        self.b_cat_ent.pack(fill="x", pady=(2, 15))
        self.b_cat_ent.set("Tech")

        btn_add = tk.Button(form_frame, text="➕ Add Book", font=("Segoe UI", 10, "bold"),
                            bg=self.get_color("accent"), fg="#ffffff", relief="flat",
                            cursor="hand2", command=self.action_add_book)
        btn_add.pack(fill="x", pady=4, ipady=3)

        btn_del = tk.Button(form_frame, text="🗑️ Delete Selected Book", font=("Segoe UI", 10, "bold"),
                            bg=self.get_color("danger"), fg="#ffffff", relief="flat",
                            cursor="hand2", command=self.action_delete_book)
        btn_del.pack(fill="x", pady=8, ipady=3)

        hint = tk.Label(form_frame, text="💡 Tip: Double-click any row in the table to edit book details.",
                        font=("Segoe UI", 8), bg=card, fg="#64748b", wraplength=260, justify="left")
        hint.pack(side="bottom", pady=5)

        self.refresh_books_table()

    def refresh_books_table(self):
        query = self.book_search_var.get().strip().lower()
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        for b in self.db.get_books():
            match = (query in b["id"].lower() or
                     query in b["title"].lower() or
                     query in b["author"].lower() or
                     query in b["category"].lower() or
                     query in b["status"].lower())
            if match:
                self.book_tree.insert("", "end", values=(
                    b["id"], b["title"], b["author"], b["category"], b["status"]
                ))

    def action_add_book(self):
        b_id = self.b_id_ent.get().strip()
        title = self.b_title_ent.get().strip()
        author = self.b_author_ent.get().strip()
        cat = self.b_cat_ent.get().strip()

        if not b_id or not title or not author or not cat:
            messagebox.showerror("Validation Error", "All fields are required! Please fill in Book ID, Title, Author, and Category.")
            return

        ok, msg = self.db.add_book(b_id, title, author, cat)
        if ok:
            messagebox.showinfo("Success", msg)
            self.b_id_ent.delete(0, "end")
            self.b_title_ent.delete(0, "end")
            self.b_author_ent.delete(0, "end")
            self.refresh_books_table()
            self.set_status(f"Added book: {title}")
        else:
            messagebox.showerror("Error", msg)

    def action_delete_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a book from the table to delete.")
            return

        item = self.book_tree.item(selected[0])
        book_id = item["values"][0]
        title = item["values"][1]

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete book '{title}' (ID: {book_id})?"):
            return

        ok, msg = self.db.delete_book(book_id)
        if ok:
            messagebox.showinfo("Success", msg)
            self.refresh_books_table()
            self.set_status(f"Deleted book {book_id}")
        else:
            messagebox.showerror("Blocked", msg)

    def open_edit_book_dialog(self):
        selected = self.book_tree.selection()
        if not selected:
            return
        item = self.book_tree.item(selected[0])
        b_id, b_title, b_author, b_cat, b_status = item["values"]

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Edit Book - {b_id}")
        dlg.geometry("380x300")
        dlg.resizable(False, False)
        dlg.configure(bg=self.get_color("card_bg"))
        dlg.transient(self.root)
        dlg.grab_set()

        card = self.get_color("card_bg")
        fg = self.get_color("fg")

        tk.Label(dlg, text=f"Update Book details (ID: {b_id})", font=("Segoe UI", 11, "bold"),
                 bg=card, fg=self.get_color("accent")).pack(pady=12)

        f = tk.Frame(dlg, bg=card, padx=25)
        f.pack(fill="x")

        tk.Label(f, text="Title *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        t_ent = tk.Entry(f, font=("Segoe UI", 10), bg=self.get_color("bg"), fg=fg)
        t_ent.pack(fill="x", pady=(2, 8))
        t_ent.insert(0, b_title)

        tk.Label(f, text="Author *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        a_ent = tk.Entry(f, font=("Segoe UI", 10), bg=self.get_color("bg"), fg=fg)
        a_ent.pack(fill="x", pady=(2, 8))
        a_ent.insert(0, b_author)

        tk.Label(f, text="Category *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        c_ent = ttk.Combobox(f, font=("Segoe UI", 10),
                             values=["Fiction", "Non-Fiction", "Tech", "Science", "History", "Education", "Biography"])
        c_ent.pack(fill="x", pady=(2, 15))
        c_ent.set(b_cat)

        def save_changes():
            nt = t_ent.get().strip()
            na = a_ent.get().strip()
            nc = c_ent.get().strip()
            ok, msg = self.db.update_book(b_id, nt, na, nc)
            if ok:
                messagebox.showinfo("Success", msg, parent=dlg)
                dlg.destroy()
                self.refresh_books_table()
            else:
                messagebox.showerror("Error", msg, parent=dlg)

        btn = tk.Button(dlg, text="Save Changes", font=("Segoe UI", 10, "bold"),
                        bg=self.get_color("accent"), fg="#ffffff", relief="flat",
                        command=save_changes, cursor="hand2")
        btn.pack(pady=10, ipadx=10, ipady=3)

    # ---------------- 3. MEMBERS MANAGEMENT ----------------
    def render_members(self):
        self.clear_content()
        self.set_status("Members management")
        bg = self.get_color("bg")
        card = self.get_color("card_bg")
        fg = self.get_color("fg")

        # Top Bar
        top_bar = tk.Frame(self.content_frame, bg=bg)
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(top_bar, text="Registered Members", font=("Segoe UI", 16, "bold"),
                 bg=bg, fg=fg).pack(side="left")

        # Live Search
        search_f = tk.Frame(top_bar, bg=bg)
        search_f.pack(side="right")
        tk.Label(search_f, text="🔍 Search:", font=("Segoe UI", 10, "bold"), bg=bg, fg=fg).pack(side="left", padx=5)
        self.member_search_var = tk.StringVar()
        self.member_search_var.trace_add("write", lambda *args: self.refresh_members_table())
        search_ent = tk.Entry(search_f, textvariable=self.member_search_var, font=("Segoe UI", 10),
                              width=22, relief="solid", bd=1, bg=card, fg=fg)
        search_ent.pack(side="left", ipady=2)

        # Main Split
        split_f = tk.Frame(self.content_frame, bg=bg)
        split_f.pack(fill="both", expand=True)

        # Table Container
        tbl_container = tk.Frame(split_f, bg=card, highlightbackground=self.get_color("border"), highlightthickness=1)
        tbl_container.pack(side="left", fill="both", expand=True, padx=(0, 12))

        cols = ("Member ID", "Name", "Email", "Phone")
        self.member_tree = ttk.Treeview(tbl_container, columns=cols, show="headings", style="Custom.Treeview")

        for c in cols:
            self.member_tree.heading(c, text=c, command=lambda _c=c: self.sort_tree(self.member_tree, _c))
            self.member_tree.column(c, anchor="w", width=120)
        self.member_tree.column("Member ID", width=80, anchor="center")
        self.member_tree.column("Name", width=160)
        self.member_tree.column("Email", width=180)

        sb = ttk.Scrollbar(tbl_container, orient="vertical", command=self.member_tree.yview)
        self.member_tree.configure(yscrollcommand=sb.set)
        self.member_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.member_tree.bind("<Double-1>", lambda e: self.open_edit_member_dialog())

        # Form Container (Add Member)
        form_frame = tk.Frame(split_f, bg=card, width=300, padx=18, pady=15,
                              highlightbackground=self.get_color("border"), highlightthickness=1)
        form_frame.pack(side="right", fill="y")
        form_frame.pack_propagate(False)

        tk.Label(form_frame, text="Add New Member", font=("Segoe UI", 13, "bold"),
                 bg=card, fg=self.get_color("accent")).pack(anchor="w", pady=(0, 12))

        tk.Label(form_frame, text="Member ID *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.m_id_ent = tk.Entry(form_frame, font=("Segoe UI", 10), bg=bg, fg=fg, relief="solid", bd=1)
        self.m_id_ent.pack(fill="x", pady=(2, 8), ipady=2)

        tk.Label(form_frame, text="Full Name *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.m_name_ent = tk.Entry(form_frame, font=("Segoe UI", 10), bg=bg, fg=fg, relief="solid", bd=1)
        self.m_name_ent.pack(fill="x", pady=(2, 8), ipady=2)

        tk.Label(form_frame, text="Email Address *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.m_email_ent = tk.Entry(form_frame, font=("Segoe UI", 10), bg=bg, fg=fg, relief="solid", bd=1)
        self.m_email_ent.pack(fill="x", pady=(2, 8), ipady=2)

        tk.Label(form_frame, text="Phone Number *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.m_phone_ent = tk.Entry(form_frame, font=("Segoe UI", 10), bg=bg, fg=fg, relief="solid", bd=1)
        self.m_phone_ent.pack(fill="x", pady=(2, 15), ipady=2)

        btn_add = tk.Button(form_frame, text="➕ Register Member", font=("Segoe UI", 10, "bold"),
                            bg=self.get_color("accent"), fg="#ffffff", relief="flat",
                            cursor="hand2", command=self.action_add_member)
        btn_add.pack(fill="x", pady=4, ipady=3)

        btn_hist = tk.Button(form_frame, text="📜 View Member History", font=("Segoe UI", 10, "bold"),
                             bg=self.get_color("sidebar_active"), fg=self.get_color("sidebar_fg"), relief="flat",
                             cursor="hand2", command=self.view_selected_member_history)
        btn_hist.pack(fill="x", pady=8, ipady=3)

        hint = tk.Label(form_frame, text="💡 Tip: Double-click a row to edit details, or select and click 'View Member History' to check issued books.",
                        font=("Segoe UI", 8), bg=card, fg="#64748b", wraplength=260, justify="left")
        hint.pack(side="bottom", pady=5)

        self.refresh_members_table()

    def refresh_members_table(self):
        query = self.member_search_var.get().strip().lower()
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)

        for m in self.db.get_members():
            match = (query in m["id"].lower() or
                     query in m["name"].lower() or
                     query in m["email"].lower() or
                     query in m["phone"].lower())
            if match:
                self.member_tree.insert("", "end", values=(
                    m["id"], m["name"], m["email"], m["phone"]
                ))

    def action_add_member(self):
        mid = self.m_id_ent.get().strip()
        name = self.m_name_ent.get().strip()
        email = self.m_email_ent.get().strip()
        phone = self.m_phone_ent.get().strip()

        if not mid or not name or not email or not phone:
            messagebox.showerror("Validation Error", "All fields are required! Please fill in Member ID, Name, Email, and Phone.")
            return

        ok, msg = self.db.add_member(mid, name, email, phone)
        if ok:
            messagebox.showinfo("Success", msg)
            self.m_id_ent.delete(0, "end")
            self.m_name_ent.delete(0, "end")
            self.m_email_ent.delete(0, "end")
            self.m_phone_ent.delete(0, "end")
            self.refresh_members_table()
            self.set_status(f"Added member: {name}")
        else:
            messagebox.showerror("Error", msg)

    def open_edit_member_dialog(self):
        selected = self.member_tree.selection()
        if not selected:
            return
        item = self.member_tree.item(selected[0])
        mid, mname, memail, mphone = item["values"]

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Edit Member - {mid}")
        dlg.geometry("380x300")
        dlg.resizable(False, False)
        dlg.configure(bg=self.get_color("card_bg"))
        dlg.transient(self.root)
        dlg.grab_set()

        card = self.get_color("card_bg")
        fg = self.get_color("fg")

        tk.Label(dlg, text=f"Update Member (ID: {mid})", font=("Segoe UI", 11, "bold"),
                 bg=card, fg=self.get_color("accent")).pack(pady=12)

        f = tk.Frame(dlg, bg=card, padx=25)
        f.pack(fill="x")

        tk.Label(f, text="Full Name *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        n_ent = tk.Entry(f, font=("Segoe UI", 10), bg=self.get_color("bg"), fg=fg)
        n_ent.pack(fill="x", pady=(2, 8))
        n_ent.insert(0, mname)

        tk.Label(f, text="Email *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        e_ent = tk.Entry(f, font=("Segoe UI", 10), bg=self.get_color("bg"), fg=fg)
        e_ent.pack(fill="x", pady=(2, 8))
        e_ent.insert(0, memail)

        tk.Label(f, text="Phone *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        p_ent = tk.Entry(f, font=("Segoe UI", 10), bg=self.get_color("bg"), fg=fg)
        p_ent.pack(fill="x", pady=(2, 15))
        p_ent.insert(0, mphone)

        def save_changes():
            nn = n_ent.get().strip()
            ne = e_ent.get().strip()
            np = p_ent.get().strip()
            ok, msg = self.db.update_member(mid, nn, ne, np)
            if ok:
                messagebox.showinfo("Success", msg, parent=dlg)
                dlg.destroy()
                self.refresh_members_table()
            else:
                messagebox.showerror("Error", msg, parent=dlg)

        btn = tk.Button(dlg, text="Save Changes", font=("Segoe UI", 10, "bold"),
                        bg=self.get_color("accent"), fg="#ffffff", relief="flat",
                        command=save_changes, cursor="hand2")
        btn.pack(pady=10, ipadx=10, ipady=3)

    def view_selected_member_history(self):
        selected = self.member_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a member to view borrowing history.")
            return

        item = self.member_tree.item(selected[0])
        mid, mname = item["values"][0], item["values"][1]

        history = self.db.get_member_history(mid)

        dlg = tk.Toplevel(self.root)
        dlg.title(f"History: {mname} ({mid})")
        dlg.geometry("750x420")
        dlg.configure(bg=self.get_color("bg"))
        dlg.transient(self.root)

        card = self.get_color("card_bg")
        fg = self.get_color("fg")

        tk.Label(dlg, text=f"Borrowing History for {mname} ({mid})", font=("Segoe UI", 12, "bold"),
                 bg=self.get_color("bg"), fg=fg).pack(anchor="w", padx=15, pady=10)

        tbl_f = tk.Frame(dlg, bg=card, highlightbackground=self.get_color("border"), highlightthickness=1)
        tbl_f.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        cols = ("Book ID", "Title", "Issue Date", "Due Date", "Status", "Return Date", "Fine (Rs.)")
        tree = ttk.Treeview(tbl_f, columns=cols, show="headings", style="Custom.Treeview")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=95)
        tree.column("Title", anchor="w", width=160)

        sb = ttk.Scrollbar(tbl_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        if not history:
            tree.insert("", "end", values=("No records", "-", "-", "-", "-", "-", "-"))
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

    # ---------------- 4. ISSUE & RETURN ----------------
    def render_issue_return(self):
        self.clear_content()
        self.set_status("Issue & Return System")
        bg = self.get_color("bg")
        card = self.get_color("card_bg")
        fg = self.get_color("fg")

        # Top Bar
        tk.Label(self.content_frame, text="Book Issue & Return Circulation",
                 font=("Segoe UI", 16, "bold"), bg=bg, fg=fg).pack(anchor="w", pady=(0, 15))

        top_panels = tk.Frame(self.content_frame, bg=bg)
        top_panels.pack(fill="x", pady=(0, 15))

        # Panel 1: Issue Book Form
        p1 = tk.Frame(top_panels, bg=card, padx=15, pady=12,
                      highlightbackground=self.get_color("border"), highlightthickness=1)
        p1.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(p1, text="Issue a Book (14-Day Due Date)", font=("Segoe UI", 12, "bold"),
                 bg=card, fg=self.get_color("accent")).pack(anchor="w", pady=(0, 8))

        avail_books = [f"{b['id']} | {b['title']}" for b in self.db.get_books() if b.get("status") == "Available"]
        members_list = [f"{m['id']} | {m['name']}" for m in self.db.get_members()]

        tk.Label(p1, text="Select Available Book *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.issue_book_cb = ttk.Combobox(p1, values=avail_books, state="readonly" if avail_books else "normal", font=("Segoe UI", 9))
        self.issue_book_cb.pack(fill="x", pady=(2, 6))
        if avail_books:
            self.issue_book_cb.current(0)

        tk.Label(p1, text="Select Member *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.issue_member_cb = ttk.Combobox(p1, values=members_list, state="readonly" if members_list else "normal", font=("Segoe UI", 9))
        self.issue_member_cb.pack(fill="x", pady=(2, 6))
        if members_list:
            self.issue_member_cb.current(0)

        # Dates Display
        today = date.today()
        due = today + timedelta(days=14)

        date_f = tk.Frame(p1, bg=card)
        date_f.pack(fill="x", pady=6)
        tk.Label(date_f, text=f"Issue Date: {today.strftime('%Y-%m-%d')}", font=("Segoe UI", 9), bg=card, fg="#64748b").pack(side="left")
        tk.Label(date_f, text=f"Due Date: {due.strftime('%Y-%m-%d')}", font=("Segoe UI", 9, "bold"), bg=card, fg=self.get_color("success")).pack(side="right")

        btn_issue = tk.Button(p1, text="📤 Issue Book", font=("Segoe UI", 10, "bold"),
                              bg=self.get_color("accent"), fg="#ffffff", relief="flat",
                              cursor="hand2", command=lambda: self.action_issue_book(today, due))
        btn_issue.pack(fill="x", pady=(8, 4), ipady=3)

        # Panel 2: Return Book Form
        p2 = tk.Frame(top_panels, bg=card, padx=15, pady=12,
                      highlightbackground=self.get_color("border"), highlightthickness=1)
        p2.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(p2, text="Return a Book & Calculate Fine", font=("Segoe UI", 12, "bold"),
                 bg=card, fg=self.get_color("warning")).pack(anchor="w", pady=(0, 8))

        active_issues = self.db.get_active_issues()
        issued_options = [f"{i['book_id']} | {i['book_title']} (by {i['member_name']})" for i in active_issues]

        tk.Label(p2, text="Select Issued Book to Return *", font=("Segoe UI", 9, "bold"), bg=card, fg=fg).pack(anchor="w")
        self.return_book_cb = ttk.Combobox(p2, values=issued_options, state="readonly" if issued_options else "normal", font=("Segoe UI", 9))
        self.return_book_cb.pack(fill="x", pady=(2, 6))
        if issued_options:
            self.return_book_cb.current(0)

        policy_lbl = tk.Label(p2, text="⚠️ Late Fine Policy: Rs. 2 per day past due date.",
                              font=("Segoe UI", 9, "italic"), bg=card, fg="#f59e0b")
        policy_lbl.pack(anchor="w", pady=6)

        btn_return = tk.Button(p2, text="📥 Return Book & Calculate Fine", font=("Segoe UI", 10, "bold"),
                               bg=self.get_color("success"), fg="#ffffff", relief="flat",
                               cursor="hand2", command=self.action_return_book)
        btn_return.pack(fill="x", pady=(18, 4), ipady=3)

        # Bottom Active Issues Table
        tk.Label(self.content_frame, text="Active Issued Books Records (Red = Overdue)",
                 font=("Segoe UI", 12, "bold"), bg=bg, fg=fg).pack(anchor="w", pady=(5, 6))

        tbl_f = tk.Frame(self.content_frame, bg=card, highlightbackground=self.get_color("border"), highlightthickness=1)
        tbl_f.pack(fill="both", expand=True)

        cols = ("Book ID", "Title", "Member ID", "Member Name", "Issue Date", "Due Date", "Days Remaining / Overdue")
        self.issue_tree = ttk.Treeview(tbl_f, columns=cols, show="headings", style="Custom.Treeview")

        for c in cols:
            self.issue_tree.heading(c, text=c, command=lambda _c=c: self.sort_tree(self.issue_tree, _c))
            self.issue_tree.column(c, anchor="center", width=110)
        self.issue_tree.column("Title", anchor="w", width=180)
        self.issue_tree.column("Member Name", anchor="w", width=140)

        sb = ttk.Scrollbar(tbl_f, orient="vertical", command=self.issue_tree.yview)
        self.issue_tree.configure(yscrollcommand=sb.set)
        self.issue_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.issue_tree.tag_configure("overdue", background=self.get_color("overdue_bg"), foreground=self.get_color("overdue_fg"))

        for iss in active_issues:
            due_d = datetime.strptime(iss["due_date"], "%Y-%m-%d").date()
            days_diff = (due_d - today).days
            if days_diff < 0:
                status_text = f"OVERDUE by {abs(days_diff)} days (Fine: Rs. {abs(days_diff)*2})"
                tag = "overdue"
            else:
                status_text = f"{days_diff} days left"
                tag = ""

            self.issue_tree.insert("", "end", values=(
                iss["book_id"], iss["book_title"], iss["member_id"], iss["member_name"],
                iss["issue_date"], iss["due_date"], status_text
            ), tags=(tag,) if tag else ())

    def action_issue_book(self, today, due):
        book_selection = self.issue_book_cb.get().strip()
        member_selection = self.issue_member_cb.get().strip()

        if not book_selection or not member_selection:
            messagebox.showerror("Error", "Please select both a book and a member to issue!")
            return

        book_id = book_selection.split("|")[0].strip()
        member_id = member_selection.split("|")[0].strip()

        ok, msg = self.db.issue_book(book_id, member_id, today.strftime("%Y-%m-%d"), due.strftime("%Y-%m-%d"))
        if ok:
            messagebox.showinfo("Success", msg)
            self.render_issue_return()
            self.set_status(f"Issued book {book_id} to member {member_id}")
        else:
            messagebox.showerror("Error", msg)

    def action_return_book(self):
        ret_selection = self.return_book_cb.get().strip()
        if not ret_selection:
            messagebox.showerror("Error", "Please select an issued book to return!")
            return

        book_id = ret_selection.split("|")[0].strip()
        if not messagebox.askyesno("Confirm Return", f"Confirm return of book ID: {book_id}?"):
            return

        ok, fine, msg = self.db.return_book(book_id)
        if ok:
            if fine > 0:
                messagebox.showwarning("Return with Fine", msg)
            else:
                messagebox.showinfo("Return Successful", msg)
            self.render_issue_return()
            self.set_status(f"Returned book {book_id} | Fine: Rs. {fine}")
        else:
            messagebox.showerror("Error", msg)

    # ---------------- TABLE COLUMN SORTING ----------------
    def sort_tree(self, tree, col):
        current_dir = self.sort_directions.get(col, False)
        reverse = not current_dir
        self.sort_directions[col] = reverse

        items = [(tree.set(k, col), k) for k in tree.get_children("")]

        # Check numeric sorting if applicable
        def convert_val(val):
            # Try float/int
            try:
                # Remove prefixes or currency signs like Rs.
                clean = val.replace("Rs.", "").replace("OVERDUE by", "").replace("days remaining", "").strip()
                return float(clean.split()[0])
            except Exception:
                return val.lower()

        items.sort(key=lambda t: convert_val(t[0]), reverse=reverse)

        for index, (val, k) in enumerate(items):
            tree.move(k, "", index)

        # Update heading arrow indicator
        for c in tree["columns"]:
            heading_txt = c
            if c == col:
                heading_txt += " ▲" if not reverse else " ▼"
            tree.heading(c, text=heading_txt)

def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
