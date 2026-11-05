import json
import os
from datetime import datetime, date

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library_data.json")

DEFAULT_DATA = {
    "users": {
        "admin": "admin123"
    },
    "books": [
        {"id": "B101", "title": "To Kill a Mockingbird", "author": "Harper Lee", "category": "Fiction", "status": "Available"},
        {"id": "B102", "title": "Clean Code", "author": "Robert C. Martin", "category": "Tech", "status": "Available"},
        {"id": "B103", "title": "A Brief History of Time", "author": "Stephen Hawking", "category": "Science", "status": "Available"},
        {"id": "B104", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "category": "Fiction", "status": "Available"},
        {"id": "B105", "title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "category": "Education", "status": "Available"}
    ],
    "members": [
        {"id": "M001", "name": "John Doe", "email": "john@example.com", "phone": "9876543210"},
        {"id": "M002", "name": "Alice Smith", "email": "alice@example.com", "phone": "9123456780"},
        {"id": "M003", "name": "Subhankar Biswal", "email": "subhankar@example.com", "phone": "9988776655"}
    ],
    "issues": [],
    "issue_history": []
}

class Database:
    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = DEFAULT_DATA.copy()
                self.save()
        else:
            self.data = DEFAULT_DATA.copy()
            self.save()

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    # Auth methods
    def verify_login(self, username, password):
        users = self.data.get("users", {})
        return users.get(username) == password

    def change_password(self, username, old_password, new_password):
        if not self.verify_login(username, old_password):
            return False, "Current password does not match!"
        if len(new_password) < 4:
            return False, "New password must be at least 4 characters!"
        self.data["users"][username] = new_password
        self.save()
        return True, "Password changed successfully!"

    # Stats
    def get_stats(self):
        books = self.data.get("books", [])
        members = self.data.get("members", [])
        total_books = len(books)
        issued_books = sum(1 for b in books if b.get("status") == "Issued")
        available_books = total_books - issued_books
        total_members = len(members)
        return {
            "total_books": total_books,
            "available_books": available_books,
            "issued_books": issued_books,
            "total_members": total_members
        }

    # Books
    def get_books(self):
        return self.data.get("books", [])

    def add_book(self, book_id, title, author, category):
        book_id = book_id.strip()
        title = title.strip()
        author = author.strip()
        category = category.strip()

        if not book_id or not title or not author or not category:
            return False, "All fields are required!"

        for b in self.data["books"]:
            if b["id"].lower() == book_id.lower():
                return False, f"Book ID '{book_id}' already exists!"
            if b["title"].strip().lower() == title.lower() and b["author"].strip().lower() == author.lower():
                return False, f"Duplicate: Book '{title}' by '{author}' is already registered!"

        new_book = {
            "id": book_id,
            "title": title,
            "author": author,
            "category": category,
            "status": "Available"
        }
        self.data["books"].append(new_book)
        self.save()
        return True, "Book added successfully!"

    def update_book(self, book_id, title, author, category):
        title = title.strip()
        author = author.strip()
        category = category.strip()
        if not title or not author or not category:
            return False, "Title, Author, and Category cannot be empty!"

        for b in self.data["books"]:
            if b["id"] == book_id:
                # Duplicate check excluding self
                for other in self.data["books"]:
                    if other["id"] != book_id and other["title"].strip().lower() == title.lower() and other["author"].strip().lower() == author.lower():
                        return False, f"Another book with title '{title}' and author '{author}' already exists!"
                b["title"] = title
                b["author"] = author
                b["category"] = category
                self.save()
                return True, "Book updated successfully!"
        return False, "Book not found!"

    def delete_book(self, book_id):
        book = next((b for b in self.data["books"] if b["id"] == book_id), None)
        if not book:
            return False, "Book not found!"
        if book.get("status") == "Issued":
            return False, "Cannot delete an issued book! Please return it first."
        
        self.data["books"] = [b for b in self.data["books"] if b["id"] != book_id]
        self.save()
        return True, "Book deleted successfully!"

    # Members
    def get_members(self):
        return self.data.get("members", [])

    def add_member(self, member_id, name, email, phone):
        member_id = member_id.strip()
        name = name.strip()
        email = email.strip()
        phone = phone.strip()

        if not member_id or not name or not email or not phone:
            return False, "All fields are required!"

        for m in self.data["members"]:
            if m["id"].lower() == member_id.lower():
                return False, f"Member ID '{member_id}' already exists!"
            if m["email"].lower() == email.lower():
                return False, f"Member with email '{email}' already exists!"

        new_member = {
            "id": member_id,
            "name": name,
            "email": email,
            "phone": phone
        }
        self.data["members"].append(new_member)
        self.save()
        return True, "Member registered successfully!"

    def update_member(self, member_id, name, email, phone):
        name = name.strip()
        email = email.strip()
        phone = phone.strip()

        if not name or not email or not phone:
            return False, "Fields cannot be empty!"

        for m in self.data["members"]:
            if m["id"] == member_id:
                for other in self.data["members"]:
                    if other["id"] != member_id and other["email"].strip().lower() == email.lower():
                        return False, f"Another member with email '{email}' already exists!"
                m["name"] = name
                m["email"] = email
                m["phone"] = phone
                self.save()
                return True, "Member updated successfully!"
        return False, "Member not found!"

    # Issue / Return
    def get_active_issues(self):
        return self.data.get("issues", [])

    def get_member_history(self, member_id):
        history = [h for h in self.data.get("issue_history", []) if h.get("member_id") == member_id]
        active = [h for h in self.data.get("issues", []) if h.get("member_id") == member_id]
        return active + history

    def issue_book(self, book_id, member_id, issue_date_str, due_date_str):
        book = next((b for b in self.data["books"] if b["id"] == book_id), None)
        member = next((m for m in self.data["members"] if m["id"] == member_id), None)

        if not book:
            return False, "Selected book does not exist!"
        if not member:
            return False, "Selected member does not exist!"
        if book.get("status") == "Issued":
            return False, "Book is already issued to someone else!"

        issue_record = {
            "issue_id": f"ISS-{int(datetime.now().timestamp())}",
            "book_id": book_id,
            "book_title": book["title"],
            "member_id": member_id,
            "member_name": member["name"],
            "issue_date": issue_date_str,
            "due_date": due_date_str,
            "status": "Issued"
        }

        book["status"] = "Issued"
        self.data["issues"].append(issue_record)
        self.save()
        return True, f"Book '{book['title']}' issued to {member['name']} successfully!"

    def return_book(self, book_id):
        issue_idx = next((i for i, iss in enumerate(self.data["issues"]) if iss["book_id"] == book_id), None)
        if issue_idx is None:
            return False, 0, "No active issue found for this book!"

        record = self.data["issues"].pop(issue_idx)
        today = date.today()
        due_d = datetime.strptime(record["due_date"], "%Y-%m-%d").date()

        days_late = (today - due_d).days
        fine = max(0, days_late * 2)

        # Update book status
        for b in self.data["books"]:
            if b["id"] == book_id:
                b["status"] = "Available"
                break

        record["return_date"] = today.strftime("%Y-%m-%d")
        record["status"] = "Returned"
        record["fine"] = fine
        record["days_late"] = max(0, days_late)

        self.data.setdefault("issue_history", []).append(record)
        self.save()

        msg = f"Book '{record['book_title']}' returned successfully."
        if fine > 0:
            msg += f"\nLate by {days_late} days. Total Late Fine: Rs. {fine}"
        else:
            msg += "\nReturned on time. No late fine applied."
        return True, fine, msg

