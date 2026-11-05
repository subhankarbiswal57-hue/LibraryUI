# 📚 LibraryUI - Desktop Library Management System

A desktop Library Management System built using Python and Tkinter (`tkinter` / `ttk`).

---

## ✨ Features Checklist

### 🔐 Authentication & Session
- **Login screen**: Username and password check with error popup on invalid credentials.
- **Change Password**: In-app secure dialog to update credentials.
- **Logout**: Confirmation popup before terminating current session.

### 📊 Dashboard
- **Live Counter Cards**: Displays Total Books, Available Books, Issued Books, and Total Members.
- **Overdue Monitoring**: Real-time listing of active issues with red highlights for overdue books and calculation of pending fines.

### 📖 Books Management
- **Table view**: Clean columnar display of ID, Title, Author, Category, and Status.
- **Live Search**: Instant dynamic filtering as you type across ID, title, author, and category.
- **Add Book**: Validated entry form with duplicate checks (blocks duplicate title & author pairs or duplicate IDs).
- **Edit Book**: Double-click any row to edit book details.
- **Delete Book**: Validation popup, strictly blocking deletion if the book is currently marked as **Issued**.

### 👥 Members Management
- **Table view**: View all registered members.
- **Live Search**: Instant filter by member ID, name, email, or phone.
- **Add Member**: Validated form with duplicate email and ID prevention.
- **Edit Member**: Double-click row to update name, email, or contact number.
- **Member History**: View complete history of active and previously returned books for any member.

### 🔄 Issue & Return Circulation
- **Issue Book**: Pick an available book and a member with an automated 14-day due date calculation.
- **Return Book**: Process returns with late fine calculation at **Rs. 2 per day** past the due date.
- **Overdue Highlight**: Overdue books highlighted in distinctive red styling.

### 🎨 Polish & Extras
- **Dark Mode Toggle**: One-click switch between Modern Light and Dark themes.
- **Table Column Sorting**: Click any table column header to sort ascending or descending.
- **Status Bar & Menu Bar**: Persistent status information, File, View, and Help menus.
- **Data Persistence**: Auto-saves and loads from `library_data.json`.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (Tkinter included by default in standard Python installations)

### Running the Application

```bash
cd LibraryUI
python main.py
```

### Default Credentials
- **Username:** `admin`
- **Password:** `admin123`
