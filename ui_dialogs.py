"""
Modern Dialogs and Notification Modals for LibraryUI
Provides cohesive SaaS-styled modal dialogs, confirmations, and toast/banner feedback.
"""

import customtkinter as ctk
from ui_theme import Theme

class ModernDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Dialog", width=420, height=320):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()
        
        # Center over parent window
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + max(0, (pw - width) // 2)
            y = py + max(0, (ph - height) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass


class ConfirmModal(ctk.CTkToplevel):
    """Modern modal dialog returning True/False."""
    def __init__(self, parent, title="Confirm", message="", confirm_text="Confirm", cancel_text="Cancel", is_danger=False):
        super().__init__(parent)
        self.result = False
        self.title(title)
        self.geometry("420x220")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()

        # Center over parent
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + max(0, (pw - 420) // 2)
            y = py + max(0, (ph - 220) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        content = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=12)
        content.pack(fill="both", expand=True, padx=24, pady=24)

        icon_text = "⚠️" if is_danger else "❓"
        title_lbl = ctk.CTkLabel(
            content,
            text=f"{icon_text}  {title}",
            font=(Theme.FONT_FAMILY, 18, "bold"),
            text_color=Theme.DANGER if is_danger else Theme.TEXT_PRIMARY,
            anchor="w"
        )
        title_lbl.pack(fill="x", pady=(0, 10))

        msg_lbl = ctk.CTkLabel(
            content,
            text=message,
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_SECONDARY,
            wraplength=370,
            justify="left",
            anchor="w"
        )
        msg_lbl.pack(fill="both", expand=True, pady=(0, 16))

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")

        btn_cancel = ctk.CTkButton(
            btn_row,
            text=cancel_text,
            fg_color=Theme.SURFACE_MUTED,
            text_color=Theme.TEXT_SECONDARY,
            hover_color=Theme.BORDER_LIGHT,
            corner_radius=8,
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=36,
            command=self._on_cancel
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_confirm = ctk.CTkButton(
            btn_row,
            text=confirm_text,
            fg_color=Theme.DANGER if is_danger else Theme.PRIMARY,
            text_color=Theme.TEXT_WHITE,
            hover_color=Theme.DANGER_HOVER if is_danger else Theme.PRIMARY_HOVER,
            corner_radius=8,
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=36,
            command=self._on_confirm
        )
        btn_confirm.pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window()

    def _on_confirm(self):
        self.result = True
        self.destroy()

    def _on_cancel(self):
        self.result = False
        self.destroy()

    @classmethod
    def ask(cls, parent, title="Confirm", message="", confirm_text="Confirm", cancel_text="Cancel", is_danger=False):
        dialog = cls(parent, title, message, confirm_text, cancel_text, is_danger)
        return dialog.result


class AlertModal(ctk.CTkToplevel):
    """Modern modal alert for info, success, warning, or error messages."""
    def __init__(self, parent, title="Notification", message="", kind="info"):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x210")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + max(0, (pw - 420) // 2)
            y = py + max(0, (ph - 210) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        color_map = {
            "success": (Theme.SUCCESS, "✅"),
            "error": (Theme.DANGER, "❌"),
            "warning": (Theme.WARNING, "⚠️"),
            "info": (Theme.PRIMARY, "ℹ️"),
        }
        color, icon = color_map.get(kind, (Theme.PRIMARY, "ℹ️"))

        content = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=12)
        content.pack(fill="both", expand=True, padx=24, pady=24)

        header = ctk.CTkLabel(
            content,
            text=f"{icon}  {title}",
            font=(Theme.FONT_FAMILY, 17, "bold"),
            text_color=color,
            anchor="w"
        )
        header.pack(fill="x", pady=(0, 10))

        msg_lbl = ctk.CTkLabel(
            content,
            text=message,
            font=(Theme.FONT_FAMILY, 13),
            text_color=Theme.TEXT_SECONDARY,
            wraplength=370,
            justify="left",
            anchor="w"
        )
        msg_lbl.pack(fill="both", expand=True, pady=(0, 16))

        btn_ok = ctk.CTkButton(
            content,
            text="Dismiss",
            fg_color=color,
            text_color=Theme.TEXT_WHITE,
            hover_color=Theme.PRIMARY_HOVER if kind == "info" else None,
            corner_radius=8,
            font=(Theme.FONT_FAMILY, 12, "bold"),
            height=34,
            width=100,
            command=self.destroy
        )
        btn_ok.pack(side="bottom", anchor="e")

        self.wait_window()

    @classmethod
    def show_info(cls, parent, title, message):
        cls(parent, title, message, kind="info")

    @classmethod
    def show_success(cls, parent, title, message):
        cls(parent, title, message, kind="success")

    @classmethod
    def show_warning(cls, parent, title, message):
        cls(parent, title, message, kind="warning")

    @classmethod
    def show_error(cls, parent, title, message):
        cls(parent, title, message, kind="error")
