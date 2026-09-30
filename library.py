"""
Library Management System
-------------------------
A simple console-based project using only Python's standard library.
Features: add/view/search/delete books, add members, issue & return books,
fine calculation, and automatic saving to a JSON file.
"""

import json
import os
from datetime import datetime, timedelta

DATA_FILE = "library_data.json"
LOAN_DAYS = 14        # days a book can be kept
FINE_PER_DAY = 2      # fine (Rs.) per late day
DATE_FMT = "%Y-%m-%d"


class Library:
    def __init__(self):
        self.books = {}     # book_id -> {title, author, copies, available}
        self.members = {}   # member_id -> {name, issued: {book_id: due_date}}
        self.load()

    # ---------- storage ----------
    def load(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            self.books = data.get("books", {})
            self.members = data.get("members", {})

    def save(self):
        with open(DATA_FILE, "w") as f:
            json.dump({"books": self.books, "members": self.members}, f, indent=4)

    # ---------- books ----------
    def add_book(self, book_id, title, author, copies):
        if book_id in self.books:
            print("A book with this ID already exists.")
            return
        self.books[book_id] = {
            "title": title, "author": author,
            "copies": copies, "available": copies,
        }
        self.save()
        print(f"Book '{title}' added.")

    def view_books(self):
        if not self.books:
            print("No books in the library.")
            return
        print(f"\n{'ID':<8}{'Title':<30}{'Author':<22}{'Available':<10}")
        print("-" * 70)
        for bid, b in self.books.items():
            print(f"{bid:<8}{b['title']:<30}{b['author']:<22}{b['available']}/{b['copies']}")

    def search_book(self, keyword):
        keyword = keyword.lower()
        found = False
        for bid, b in self.books.items():
            if keyword in b["title"].lower() or keyword in b["author"].lower():
                print(f"{bid}: {b['title']} by {b['author']} "
                      f"({b['available']}/{b['copies']} available)")
                found = True
        if not found:
            print("No matching books found.")

    def delete_book(self, book_id):
        if book_id not in self.books:
            print("Book not found.")
            return
        b = self.books[book_id]
        if b["available"] != b["copies"]:
            print("Cannot delete: some copies are currently issued.")
            return
        del self.books[book_id]
        self.save()
        print("Book deleted.")

    # ---------- members ----------
    def add_member(self, member_id, name):
        if member_id in self.members:
            print("A member with this ID already exists.")
            return
        self.members[member_id] = {"name": name, "issued": {}}
        self.save()
        print(f"Member '{name}' added.")

    def view_members(self):
        if not self.members:
            print("No members registered.")
            return
        for mid, m in self.members.items():
            print(f"{mid}: {m['name']} - books issued: {len(m['issued'])}")

    # ---------- issue / return ----------
    def issue_book(self, member_id, book_id):
        if member_id not in self.members:
            print("Member not found.")
            return
        if book_id not in self.books:
            print("Book not found.")
            return
        book = self.books[book_id]
        member = self.members[member_id]
        if book["available"] < 1:
            print("Sorry, no copies available right now.")
            return
        if book_id in member["issued"]:
            print("This member already has this book.")
            return
        due = datetime.now() + timedelta(days=LOAN_DAYS)
        member["issued"][book_id] = due.strftime(DATE_FMT)
        book["available"] -= 1
        self.save()
        print(f"Issued '{book['title']}' to {member['name']}. "
              f"Due date: {due.strftime(DATE_FMT)}")

    def return_book(self, member_id, book_id):
        if member_id not in self.members:
            print("Member not found.")
            return
        member = self.members[member_id]
        if book_id not in member["issued"]:
            print("This member has not issued that book.")
            return
        due = datetime.strptime(member["issued"].pop(book_id), DATE_FMT)
        self.books[book_id]["available"] += 1
        late_days = (datetime.now() - due).days
        if late_days > 0:
            print(f"Returned {late_days} day(s) late. Fine: Rs. {late_days * FINE_PER_DAY}")
        else:
            print("Book returned on time. No fine.")
        self.save()


def ask_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def menu():
    print("""
========== LIBRARY MANAGEMENT SYSTEM ==========
1. Add Book            6. Add Member
2. View Books          7. View Members
3. Search Book         8. Issue Book
4. Delete Book         9. Return Book
5. Exit
===============================================""")


def main():
    lib = Library()
    while True:
        menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            lib.add_book(input("Book ID: "), input("Title: "),
                         input("Author: "), ask_int("Copies: "))
        elif choice == "2":
            lib.view_books()
        elif choice == "3":
            lib.search_book(input("Enter title or author: "))
        elif choice == "4":
            lib.delete_book(input("Book ID to delete: "))
        elif choice == "5":
            print("Goodbye!")
            break
        elif choice == "6":
            lib.add_member(input("Member ID: "), input("Name: "))
        elif choice == "7":
            lib.view_members()
        elif choice == "8":
            lib.issue_book(input("Member ID: "), input("Book ID: "))
        elif choice == "9":
            lib.return_book(input("Member ID: "), input("Book ID: "))
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()