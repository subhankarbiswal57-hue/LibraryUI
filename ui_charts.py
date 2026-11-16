"""
UI Components: Charts using Matplotlib embedded in Tkinter/CustomTkinter.
Renders clean SaaS style doughnut charts for book availability and bar charts for categories.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from ui_theme import Theme

class AnalyticsCharts(ctk.CTkFrame):
    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_LIGHT, **kwargs)
        self.db = db
        self.canvas = None
        self.fig = None
        
        # Header inside chart card
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 4))
        
        title = ctk.CTkLabel(
            header,
            text="📈 Library Analytics & Distribution",
            font=(Theme.FONT_FAMILY, 15, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left")

        # Container for matplotlib canvas
        self.chart_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        
        self.render_charts()

    def render_charts(self):
        # Clear previous canvas if exists
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        stats = self.db.get_stats()
        books = self.db.get_books()
        
        # Setup Figure with 2 subplots: Doughnut & Horizontal Bar
        plt.rcParams['font.sans-serif'] = 'Segoe UI'
        plt.rcParams['font.family'] = 'sans-serif'
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.2), facecolor="#FFFFFF")
        fig.subplots_adjust(wspace=0.35, left=0.06, right=0.96, top=0.88, bottom=0.14)
        
        # 1. Doughnut Chart: Inventory Status
        avail = stats["available_books"]
        issued = stats["issued_books"]
        total = stats["total_books"]
        
        if total == 0:
            ax1.text(0.5, 0.5, "No Books in Inventory", horizontalalignment='center', verticalalignment='center', color="#94A3B8")
            ax1.axis('off')
        else:
            slices = [avail, issued]
            labels = [f"Available ({avail})", f"Issued ({issued})"]
            colors = ["#10B981", "#F59E0B"]
            
            # Filter zero slices
            active_slices = []
            active_labels = []
            active_colors = []
            for s, l, c in zip(slices, labels, colors):
                if s > 0:
                    active_slices.append(s)
                    active_labels.append(l)
                    active_colors.append(c)

            wedges, texts, autotexts = ax1.pie(
                active_slices,
                labels=active_labels,
                autopct='%1.0f%%',
                startangle=140,
                colors=active_colors,
                pctdistance=0.75,
                textprops=dict(color="#334155", size=9, weight="bold"),
                wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2)
            )
            for autotext in autotexts:
                autotext.set_color('#FFFFFF')
                autotext.set_fontsize(9)
                autotext.set_weight('bold')
                
            ax1.set_title("Circulation Status", fontsize=11, fontweight="bold", color="#1E293B", pad=8)

        # 2. Bar Chart: Books by Category
        cat_counts = {}
        for b in books:
            c = b.get("category", "Other") or "Other"
            cat_counts[c] = cat_counts.get(c, 0) + 1
            
        if not cat_counts:
            ax2.text(0.5, 0.5, "No Categories", horizontalalignment='center', verticalalignment='center', color="#94A3B8")
            ax2.axis('off')
        else:
            categories = list(cat_counts.keys())
            counts = list(cat_counts.values())
            
            # Palette
            bar_colors = ["#3B82F6", "#8B5CF6", "#06B6D4", "#EC4899", "#10B981", "#F59E0B", "#6366F1"]
            bar_colors = (bar_colors * ((len(categories) // len(bar_colors)) + 1))[:len(categories)]
            
            bars = ax2.bar(categories, counts, color=bar_colors, width=0.55, edgecolor="none", zorder=3)
            ax2.set_title("Books by Genre / Category", fontsize=11, fontweight="bold", color="#1E293B", pad=8)
            ax2.set_ylabel("Book Count", fontsize=9, color="#64748B", fontweight="bold")
            ax2.grid(axis='y', linestyle='--', alpha=0.35, zorder=0, color="#CBD5E1")
            
            ax2.tick_params(axis='x', rotation=18, labelsize=8.5, colors="#475569")
            ax2.tick_params(axis='y', labelsize=8.5, colors="#475569")
            
            # Remove top and right spines
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['left'].set_color('#E2E8F0')
            ax2.spines['bottom'].set_color('#E2E8F0')
            
            # Integer y-axis ticks
            max_c = max(counts) if counts else 5
            ax2.set_ylim(0, max(max_c + 1, 4))
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax2.annotate(f'{height}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 2),  # 2 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#334155')

        self.fig = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def refresh(self):
        self.render_charts()
