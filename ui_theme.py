"""
Design System and Theme Tokens for LibraryUI
SaaS-inspired color palette, typography definitions, and component styling.
"""

class Theme:
    # Font families
    FONT_FAMILY = "Segoe UI"
    
    # Core Colors - SaaS Light Aesthetic
    BG_APP = "#F8FAFC"             # Crisp light background (slate-50)
    BG_CARD = "#FFFFFF"            # White elevated card background
    BG_SIDEBAR = "#0F172A"         # Deep executive navy sidebar (slate-900)
    BG_SIDEBAR_HOVER = "#1E293B"   # Slate-800
    BG_SIDEBAR_ACTIVE = "#2563EB"  # Vibrant SaaS blue for active state
    
    # Secondary surfaces & borders
    SURFACE_MUTED = "#F1F5F9"      # Slate-100 for subtle backdrops & inputs
    BORDER_LIGHT = "#E2E8F0"       # Slate-200 border
    BORDER_SUBTLE = "#CBD5E1"      # Slate-300 border
    
    # Text colors
    TEXT_PRIMARY = "#0F172A"       # Slate-900 high contrast text
    TEXT_SECONDARY = "#475569"     # Slate-600 subheadings / labels
    TEXT_MUTED = "#94A3B8"         # Slate-400 hint / metadata text
    TEXT_WHITE = "#FFFFFF"         # Pure white text
    TEXT_SIDEBAR = "#94A3B8"       # Unselected sidebar item text
    TEXT_SIDEBAR_ACTIVE = "#FFFFFF"# Selected sidebar item text
    
    # Brand & Status Accents
    PRIMARY = "#2563EB"            # SaaS Blue (blue-600)
    PRIMARY_HOVER = "#1D4ED8"      # Blue-700
    PRIMARY_LIGHT = "#EFF6FF"      # Blue-50
    
    SUCCESS = "#10B981"            # Emerald-500
    SUCCESS_LIGHT = "#ECFDF5"      # Emerald-50
    SUCCESS_TEXT = "#065F46"       # Emerald-800
    
    WARNING = "#F59E0B"            # Amber-500
    WARNING_LIGHT = "#FFFBEB"      # Amber-50
    WARNING_TEXT = "#92400E"       # Amber-800
    
    DANGER = "#EF4444"             # Rose/Red-500
    DANGER_HOVER = "#DC2626"       # Red-600
    DANGER_LIGHT = "#FEF2F2"       # Red-50
    DANGER_TEXT = "#991B1B"        # Red-800
    
    PURPLE = "#8B5CF6"             # Purple-500
    PURPLE_LIGHT = "#F5F3FF"       # Purple-50
    PURPLE_TEXT = "#5B21B6"        # Purple-800
    
    INFO = "#0EA5E9"               # Sky-500
    INFO_LIGHT = "#F0F9FF"         # Sky-50
    
    # Overdue badges & banner styling
    OVERDUE_BG = "#FEE2E2"
    OVERDUE_FG = "#991B1B"
    OVERDUE_BORDER = "#FCA5A5"
