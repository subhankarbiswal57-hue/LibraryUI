"""
Library Management System - Modern SaaS Desktop Application
Built with Python + CustomTkinter / Tkinter + Matplotlib.

Features:
- Professional light-themed SaaS dashboard with executive dark sidebar
- Real-time statistics KPI cards and embedded Matplotlib visual analytics
- Dynamic Book Inventory with search, category filtering, dual views (Data Table & Grid cards)
- Patron Member directory with quick loan status, history modal, and profile cards
- Streamlined Issue & Return circulation desk with 14-day calculation & automated overdue fines
- Fully preserved JSON persistence (library_data.json) & database logic
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# Ensure working directory is correctly set
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import Database
from ui_theme import Theme
from ui_dialogs import ConfirmModal, AlertModal, ModernDialog
from ui_dashboard import DashboardView
from ui_books import BooksView
from ui_members import MembersView
from ui_issue_return import IssueReturnView

# Configure CustomTkinter Appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("LibraryUI — SaaS Desktop Library System")
        self.geometry("1180x760")
        self.minsize(1040, 680)
        self.configure(fg_color=Theme.BG_APP)

        self.db = Database()
        self.current_user = None
        self.current_tab = "Dashboard"
        
        self.setup_ttk_styles()
        self.show_login_screen()

    def setup_ttk_styles(self):
        """Configure modern clean styling for Tkinter Treeview elements."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "Modern.Treeview",
            background="#FFFFFF",
            foreground=Theme.TEXT_PRIMARY,
            fieldbackground="#FFFFFF",
            rowheight=32,
            borderwidth=0,
            font=(Theme.FONT_FAMILY, 10)
        )
        self.style.map(
            "Modern.Treeview",
            background=[("selected", Theme.PRIMARY_LIGHT)],
            foreground=[("selected", Theme.PRIMARY)]
        )

        self.style.configure(
            "Modern.Treeview.Heading",
            background=Theme.SURFACE_MUTED,
            foreground=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, 10, "bold"),
            padding=(10, 8),
            relief="flat",
            borderwidth=0
        )
        self.style.map(
            "Modern.Treeview.Heading",
            background=[("active", Theme.BORDER_LIGHT)]
        )

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def set_status(self, message):
        if hasattr(self, "lbl_status_msg"):
            self.lbl_status_msg.configure(text=f"User: {self.current_user or 'Guest'} • {message}")

    # =========================================================================
    # LOGIN SCREEN (Clean Elevated SaaS Card)
    # =========================================================================
    def show_login_screen(self):
        self.clear_window()
        self.config(menu="")

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Elevated White Login Card
        card = ctk.CTkFrame(
            container,
            fg_color=Theme.BG_CARD,
            corner_radius=16,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            width=420
        )
        card.pack(padx=20, pady=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=38)

        # Brand Logo / Icon Header
        logo_badge = ctk.CTkLabel(
            inner,
            text="📚",
            font=(Theme.FONT_FAMILY, 28),
            fg_color=Theme.PRIMARY_LIGHT,
            corner_radius=12,
            width=54,
            height=54
        )
        logo_badge.pack(pady=(0, 12))

        title = ctk.CTkLabel(
            inner,
            text="Welcome to LibraryUI",
            font=(Theme.FONT_FAMILY, 20, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            inner,
            text="Enter your credentials to access the console",
            font=(Theme.FONT_FAMILY, 11),
            text_color=Theme.TEXT_MUTED
        )
        subtitle.pack(pady=(2, 22))

        # Username Input
        ctk.CTkLabel(inner, text="Username", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_login_user = ctk.CTkEntry(
            inner,
            placeholder_text="Enter username",
            font=(Theme.FONT_FAMILY, 12),
            height=38,
            corner_radius=8,
            border_color=Theme.BORDER_LIGHT,
            fg_color=Theme.SURFACE_MUTED
        )
        self.ent_login_user.pack(fill="x", pady=(3, 14))
        self.ent_login_user.insert(0, "admin")

        # Password Input
        ctk.CTkLabel(inner, text="Password", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")
        self.ent_login_pwd = ctk.CTkEntry(
            inner,
            placeholder_text="Enter password",
            font=(Theme.FONT_FAMILY, 12),
            height=38,
            corner_radius=8,
            show="•",
            border_color=Theme.BORDER_LIGHT,
            fg_color=Theme.SURFACE_MUTED
        )
        self.ent_login_pwd.pack(fill="x", pady=(3, 20))
        self.ent_login_pwd.insert(0, "admin123")
        self.ent_login_pwd.bind("<Return>", lambda e: self.process_login())

        # Login Button
        btn_login = ctk.CTkButton(
            inner,
            text="Sign In to Dashboard",
            font=(Theme.FONT_FAMILY, 13, "bold"),
            height=40,
            corner_radius=8,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.process_login
        )
        btn_login.pack(fill="x", pady=(0, 14))

        # Bottom Hint Banner
        hint = ctk.CTkLabel(
            inner,
            text="Default credentials: admin / admin123",
            font=(Theme.FONT_FAMILY, 10),
            text_color=Theme.TEXT_MUTED
        )
        hint.pack()

    def process_login(self):
        u = self.ent_login_user.get().strip()
        p = self.ent_login_pwd.get()

        if not u or not p:
            AlertModal.show_error(self, "Input Required", "Please provide both Username and Password.")
            return

        if self.db.verify_login(u, p):
            self.current_user = u
            self.show_main_app()
        else:
            AlertModal.show_error(self, "Authentication Failed", "Invalid username or password! Please verify and try again.")

    # =========================================================================
    # MAIN APPLICATION LAYOUT
    # =========================================================================
    def show_main_app(self):
        self.clear_window()
        self.create_menu_bar()

        # Root layout container
        root_container = ctk.CTkFrame(self, fg_color="transparent")
        root_container.pack(fill="both", expand=True)

        # 1. Left Sidebar Navigation (Deep SaaS Slate Navy)
        self.sidebar = ctk.CTkFrame(
            root_container,
            fg_color=Theme.BG_SIDEBAR,
            corner_radius=0,
            width=230
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Header inside Sidebar
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(22, 24))

        logo_lbl = ctk.CTkLabel(
            brand_frame,
            text="📚",
            font=(Theme.FONT_FAMILY, 20),
            fg_color=Theme.PRIMARY,
            corner_radius=8,
            width=38,
            height=38
        )
        logo_lbl.pack(side="left", padx=(0, 10))

        brand_text_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_text_box.pack(side="left")

        b_name = ctk.CTkLabel(
            brand_text_box,
            text="LibraryUI",
            font=(Theme.FONT_FAMILY, 16, "bold"),
            text_color=Theme.TEXT_WHITE
        )
        b_name.pack(anchor="w")

        b_tag = ctk.CTkLabel(
            brand_text_box,
            text="SaaS Edition v2.0",
            font=(Theme.FONT_FAMILY, 9),
            text_color="#38BDF8"
        )
        b_tag.pack(anchor="w")

        # Sidebar Navigation Buttons
        nav_items = [
            ("Dashboard", "📊  Dashboard"),
            ("Books", "📖  Book Inventory"),
            ("Members", "👥  Member Directory"),
            ("IssueReturn", "🔄  Issue & Return"),
        ]

        self.nav_buttons = {}
        for tab_id, tab_label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=tab_label,
                font=(Theme.FONT_FAMILY, 12, "bold"),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color=Theme.TEXT_SIDEBAR,
                hover_color=Theme.BG_SIDEBAR_HOVER,
                command=lambda tid=tab_id: self.navigate_to(tid)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[tab_id] = btn

        # Bottom Section of Sidebar: User Profile Pill & Actions
        bot_sidebar = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bot_sidebar.pack(side="bottom", fill="x", padx=12, pady=16)

        user_card = ctk.CTkFrame(bot_sidebar, fg_color=Theme.BG_SIDEBAR_HOVER, corner_radius=8)
        user_card.pack(fill="x", pady=(0, 8))

        u_inner = ctk.CTkFrame(user_card, fg_color="transparent")
        u_inner.pack(fill="x", padx=10, pady=8)

        u_avatar = ctk.CTkLabel(
            u_inner,
            text=(self.current_user or "A")[:1].upper(),
            font=(Theme.FONT_FAMILY, 11, "bold"),
            fg_color=Theme.PRIMARY,
            text_color=Theme.TEXT_WHITE,
            corner_radius=12,
            width=26,
            height=26
        )
        u_avatar.pack(side="left", padx=(0, 8))

        u_info = ctk.CTkFrame(u_inner, fg_color="transparent")
        u_info.pack(side="left")

        u_name = ctk.CTkLabel(
            u_info,
            text=self.current_user or "Admin",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            text_color=Theme.TEXT_WHITE
        )
        u_name.pack(anchor="w")

        u_role = ctk.CTkLabel(
            u_info,
            text="Administrator",
            font=(Theme.FONT_FAMILY, 9),
            text_color="#94A3B8"
        )
        u_role.pack(anchor="w")

        btn_pwd = ctk.CTkButton(
            bot_sidebar,
            text="🔑  Change Password",
            font=(Theme.FONT_FAMILY, 11),
            anchor="w",
            height=34,
            corner_radius=6,
            fg_color="transparent",
            text_color=Theme.TEXT_SIDEBAR,
            hover_color=Theme.BG_SIDEBAR_HOVER,
            command=self.open_change_password_dialog
        )
        btn_pwd.pack(fill="x", pady=2)

        btn_logout = ctk.CTkButton(
            bot_sidebar,
            text="🚪  Sign Out",
            font=(Theme.FONT_FAMILY, 11, "bold"),
            anchor="w",
            height=34,
            corner_radius=6,
            fg_color="transparent",
            text_color="#F87171",
            hover_color=Theme.BG_SIDEBAR_HOVER,
            command=self.action_logout
        )
        btn_logout.pack(fill="x", pady=2)

        # 2. Right Work Area: Status Bar + Content Container
        right_panel = ctk.CTkFrame(root_container, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)

        # Status Bar at bottom
        status_bar = ctk.CTkFrame(right_panel, fg_color=Theme.BG_CARD, height=28, corner_radius=0, border_width=1, border_color=Theme.BORDER_LIGHT)
        status_bar.pack(side="bottom", fill="x")

        self.lbl_status_msg = ctk.CTkLabel(
            status_bar,
            text=f"User: {self.current_user} • Ready",
            font=(Theme.FONT_FAMILY, 10),
            text_color=Theme.TEXT_MUTED,
            padx=12
        )
        self.lbl_status_msg.pack(side="left")

        lbl_sys = ctk.CTkLabel(
            status_bar,
            text="Connected: JSON Database • All systems operational",
            font=(Theme.FONT_FAMILY, 10),
            text_color=Theme.SUCCESS_TEXT,
            padx=12
        )
        lbl_sys.pack(side="right")

        # Dynamic Content Frame
        self.content_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.content_frame.pack(side="top", fill="both", expand=True, padx=22, pady=18)

        # Initial view
        self.navigate_to("Dashboard")

    def navigate_to(self, tab_id):
        self.current_tab = tab_id

        # Update sidebar button active state
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(fg_color=Theme.BG_SIDEBAR_ACTIVE, text_color=Theme.TEXT_SIDEBAR_ACTIVE)
            else:
                btn.configure(fg_color="transparent", text_color=Theme.TEXT_SIDEBAR)

        # Clear existing view
        for w in self.content_frame.winfo_children():
            w.destroy()

        if tab_id == "Dashboard":
            view = DashboardView(self.content_frame, self.db, self)
            view.pack(fill="both", expand=True)
            self.set_status("Dashboard loaded")
        elif tab_id == "Books":
            view = BooksView(self.content_frame, self.db, self)
            view.pack(fill="both", expand=True)
            self.set_status("Book Inventory loaded")
        elif tab_id == "Members":
            view = MembersView(self.content_frame, self.db, self)
            view.pack(fill="both", expand=True)
            self.set_status("Member Directory loaded")
        elif tab_id == "IssueReturn":
            view = IssueReturnView(self.content_frame, self.db, self)
            view.pack(fill="both", expand=True)
            self.set_status("Circulation Desk loaded")

    def create_menu_bar(self):
        menubar = tk.Menu(self)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Reload from Disk", command=self.reload_data)
        file_menu.add_separator()
        file_menu.add_command(label="Change Password", command=self.open_change_password_dialog)
        file_menu.add_command(label="Sign Out", command=self.action_logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Navigation View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Dashboard", command=lambda: self.navigate_to("Dashboard"))
        view_menu.add_command(label="Book Inventory", command=lambda: self.navigate_to("Books"))
        view_menu.add_command(label="Member Directory", command=lambda: self.navigate_to("Members"))
        view_menu.add_command(label="Circulation Desk", command=lambda: self.navigate_to("IssueReturn"))
        menubar.add_cascade(label="View", menu=view_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About LibraryUI", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def reload_data(self):
        self.db.load()
        self.navigate_to(self.current_tab)
        AlertModal.show_success(self, "Data Synced", "Library data refreshed from disk successfully.")

    def show_about(self):
        AlertModal.show_info(
            self,
            "About LibraryUI",
            "LibraryUI — SaaS Desktop Edition v2.0\n"
            "Crafted with 100% Python, CustomTkinter, and Matplotlib.\n"
            "Features full JSON persistence, live circulation monitoring, and book & patron management."
        )

    def action_logout(self):
        confirmed = ConfirmModal.ask(
            self,
            title="Confirm Sign Out",
            message="Are you sure you want to end your current administrative session?",
            confirm_text="Sign Out",
            is_danger=True
        )
        if confirmed:
            self.current_user = None
            self.show_login_screen()

    def open_change_password_dialog(self):
        dlg = ModernDialog(self, title="Change Password", width=380, height=360)

        inner = ctk.CTkFrame(dlg, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            inner,
            text="Change Account Password",
            font=(Theme.FONT_FAMILY, 16, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(inner, text="Current Password *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        old_ent = ctk.CTkEntry(inner, show="•", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6)
        old_ent.pack(fill="x", pady=(3, 10))

        ctk.CTkLabel(inner, text="New Password *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        new_ent = ctk.CTkEntry(inner, show="•", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6)
        new_ent.pack(fill="x", pady=(3, 10))

        ctk.CTkLabel(inner, text="Confirm New Password *", font=(Theme.FONT_FAMILY, 11, "bold"), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        conf_ent = ctk.CTkEntry(inner, show="•", font=(Theme.FONT_FAMILY, 12), height=32, corner_radius=6)
        conf_ent.pack(fill="x", pady=(3, 18))

        def save_pw():
            old_p = old_ent.get()
            new_p = new_ent.get()
            conf_p = conf_ent.get()

            if not old_p or not new_p or not conf_p:
                AlertModal.show_error(dlg, "Error", "All password fields are required!")
                return
            if new_p != conf_p:
                AlertModal.show_error(dlg, "Error", "New password confirmation does not match!")
                return

            ok, msg = self.db.change_password(self.current_user, old_p, new_p)
            if ok:
                AlertModal.show_success(dlg, "Success", msg)
                dlg.destroy()
            else:
                AlertModal.show_error(dlg, "Error", msg)

        btn = ctk.CTkButton(
            inner,
            text="Update Password",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=8,
            height=36,
            command=save_pw
        )
        btn.pack(fill="x", side="bottom")

def main():
    app = LibraryApp()
    app.mainloop()

if __name__ == "__main__":
    main()
