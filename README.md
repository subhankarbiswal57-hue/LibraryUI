# 📚 LibraryUI — Modern SaaS Desktop Library System

A modern SaaS-inspired desktop Library Management Application built **100% in Python** using **CustomTkinter**, **Tkinter**, and **Matplotlib**.

---

## 🌟 Modern SaaS UI/UX Overhaul

LibraryUI combines clean SaaS light aesthetics, executive navigation, responsive data displays, visual analytics, and rock-solid local JSON persistence:

- **Executive Dark Sidebar**: Fixed deep-slate navigation bar with brand header, current active indicator tabs, user profile badge, and direct shortcut actions.
- **Light Theme SaaS Canvas**: High-contrast, clean card elevations (`#FFFFFF` on `#F8FAFC`) with subtle borders, generous whitespace, and modern typography.
- **Live Statistics & Embedded Matplotlib Analytics**:
  - Top KPI Metric Cards (Total Inventory, Available, Out on Loan, Active Patrons) with icon badges.
  - Interactive Doughnut chart showing real-time circulation breakdown (Available vs. Issued).
  - Categorical Bar chart displaying distribution across book genres.
  - Active loan monitoring with overdue tracker and automated fine calculations.
- **Book Inventory with Dual Views**:
  - **Data Table View**: Column sorting, double-click to edit, status pills, and keyboard navigation.
  - **Visual Grid View**: Responsive 2-column card layout displaying book covers, genres, availability status, and quick-action buttons.
  - **Filter & Search Bar**: Real-time debounce search across Title, Author, ID, and Genre combined with multi-criteria category and status dropdowns.
- **Patron Member Directory with Profile Cards**:
  - **SaaS Profile Cards**: Patron avatar initials, contact info badges, and active loans counter.
  - **Detailed Borrowing History**: Modal popup inspecting active loans and historical returned books with fine breakdowns.
  - **Member Table View**: Columnar view with sorting and double-click editing.
- **Circulation Desk (Issue & Return)**:
  - Side-by-side transaction stations for issuing loans and checking in returns.
  - Automated 14-day loan term calculation with calendar display.
  - Real-time late fine calculator (Rs. 2/day past due date).
  - Prominent overdue highlights with red badge tags.
- **Custom SaaS Modals & Confirmations**:
  - Non-blocking custom modal alerts and safety confirmation dialogs for destructive actions.
  - In-app Change Password dialog.
- **Zero Web Technologies**: 100% pure Python desktop app with no HTML, CSS, JavaScript, Electron, or webviews.

---

## 📁 Architecture & File Structure

```text
LibraryUI/
├── database.py             # JSON data persistence layer & business rules
├── library_data.json       # Local database store (Books, Members, Loans, Users)
├── main.py                 # Application entry point, window management & navigation
├── ui_theme.py             # SaaS design system, color tokens, and typography
├── ui_dialogs.py           # Modern CustomTkinter modal dialogs & alerts
├── ui_charts.py            # Embedded Matplotlib analytics widgets (Doughnut & Bar)
├── ui_dashboard.py         # Dashboard view with KPI cards, analytics, & overdue table
├── ui_books.py             # Book Inventory view (Table & Grid modes, Add, Edit, Delete)
├── ui_members.py           # Patron Member Directory (Cards & Table modes, History modal)
├── ui_issue_return.py      # Circulation Desk (Issue, Return, & Fine calculation)
├── requirements.txt        # Minimal Python dependencies
├── run.bat                 # One-click Windows launch script
└── README.md               # Documentation & usage guide
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher.
- Standard Tkinter support (included by default in Python for Windows).

### Installation

1. Open your terminal in the `LibraryUI` directory.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Double-click `run.bat` or run:
```bash
python main.py
```

### Default Credentials
- **Username:** `admin`
- **Password:** `admin123`

*(You can change your password anytime via the sidebar or top menu bar)*
