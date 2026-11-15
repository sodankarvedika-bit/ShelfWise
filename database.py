
import sqlite3


# 1. Connect to the database
def connect_db():
    connection = sqlite3.connect("shelfwise.db")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# 2. Create database tables
def create_tables():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT,
            quantity INTEGER NOT NULL,
            available INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (book_id) REFERENCES books(book_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            reservation_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (book_id) REFERENCES books(book_id)
        )
    """)

    connection.commit()
    connection.close()


# 3. Add a new book
def add_book(title, author, category, quantity):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO books
        (title, author, category, quantity, available)
        VALUES (?, ?, ?, ?, ?)
    """, (title, author, category, quantity, quantity))

    connection.commit()
    connection.close()


# 4. Get all books
def get_books():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    connection.close()
    return books


# 5. Search books by title or author
def search_books(keyword):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ?
    """, ('%' + keyword + '%', '%' + keyword + '%'))

    books = cursor.fetchall()

    connection.close()
    return books


# 6. Update book details
def update_book(book_id, title, author, category, quantity):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM issued_books
        WHERE book_id = ? AND return_date IS NULL
    """, (book_id,))

    borrowed = cursor.fetchone()[0]

    if quantity < borrowed:
        connection.close()
        return False

    available = quantity - borrowed

    cursor.execute("""
        UPDATE books
        SET title = ?, author = ?, category = ?,
            quantity = ?, available = ?
        WHERE book_id = ?
    """, (title, author, category, quantity, available, book_id))

    connection.commit()
    connection.close()

    return True


# 7. Delete a book

# 9. Add a new student
def add_student(name, email, department):

    connection = connect_db()
    cursor = connection.cursor()

    # Check whether email already exists
    cursor.execute(
        "SELECT student_id FROM students WHERE email = ?",
        (email,)
    )

    existing_student = cursor.fetchone()

    if existing_student:
        connection.close()
        return False

    cursor.execute("""
        INSERT INTO students (name, email, department)
        VALUES (?, ?, ?)
    """, (name, email, department))

    connection.commit()
    connection.close()

    return True


# 10. Get all students
def get_students():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    connection.close()

    return students


# 11. Search students

# 12. Issue a book to a student
def issue_book(student_id, book_id, issue_date, due_date):

    connection = connect_db()
    cursor = connection.cursor()

    # Check available copies
    cursor.execute(
        "SELECT available FROM books WHERE book_id = ?",
        (book_id,)
    )

    book = cursor.fetchone()

    if book is None or book[0] <= 0:
        connection.close()
        return False

    # Check whether student exists
    cursor.execute(
        "SELECT student_id FROM students WHERE student_id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:
        connection.close()
        return False

    # Record the issue
    cursor.execute("""
        INSERT INTO issued_books
        (student_id, book_id, issue_date, due_date)
        VALUES (?, ?, ?, ?)
    """, (student_id, book_id, issue_date, due_date))

    # Reduce available copies
    cursor.execute("""
        UPDATE books
        SET available = available - 1
        WHERE book_id = ?
    """, (book_id,))

    connection.commit()
    connection.close()

    return True


# 13. Get currently issued books
def get_active_issues():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            issued_books.issue_id,
            students.name,
            books.title,
            issued_books.issue_date,
            issued_books.due_date
        FROM issued_books
        JOIN students
        ON issued_books.student_id = students.student_id
        JOIN books
        ON issued_books.book_id = books.book_id
        WHERE issued_books.return_date IS NULL
    """)

    issues = cursor.fetchall()

    connection.close()

    return issues


# 14. Return a book

# 15. Calculate late return fine
# 16. Add a book reservation
def add_reservation(student_id, book_id, reservation_date):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO reservations
        (student_id, book_id, reservation_date, status)
        VALUES (?, ?, ?, 'Pending')
    """, (student_id, book_id, reservation_date))

    connection.commit()
    connection.close()

    return True


# 17. Get all reservations
def get_reservations():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            reservations.reservation_id,
            students.name,
            books.title,
            reservations.reservation_date,
            reservations.status
        FROM reservations
        JOIN students
        ON reservations.student_id = students.student_id
        JOIN books
        ON reservations.book_id = books.book_id
        ORDER BY reservations.reservation_id DESC
    """)

    reservations = cursor.fetchall()

    connection.close()

    return reservations


# 18. Cancel a reservation
def cancel_reservation(reservation_id):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE reservations
        SET status = 'Cancelled'
        WHERE reservation_id = ?
        AND status = 'Pending'
    """, (reservation_id,))

    connection.commit()

    success = cursor.rowcount > 0

    connection.close()

    return success
def calculate_fine(due_date, return_date=None):

    from datetime import date

    due = date.fromisoformat(due_date)

    if return_date:
        actual_return = date.fromisoformat(return_date)
    else:
        actual_return = date.today()

    late_days = max(0, (actual_return - due).days)

    fine_per_day = 5

    total_fine = late_days * fine_per_day

    return late_days, total_fine

def return_book(issue_id, return_date):

    connection = connect_db()
    cursor = connection.cursor()

    # Find the issue record
    cursor.execute("""
        SELECT book_id
        FROM issued_books
        WHERE issue_id = ? AND return_date IS NULL
    """, (issue_id,))

    issue = cursor.fetchone()

    if issue is None:
        connection.close()
        return False

    book_id = issue[0]

    # Update return date
    cursor.execute("""
        UPDATE issued_books
        SET return_date = ?
        WHERE issue_id = ?
    """, (return_date, issue_id))

    # Increase available copies
    cursor.execute("""
        UPDATE books
        SET available = available + 1
        WHERE book_id = ?
    """, (book_id,))

    connection.commit()
    connection.close()

    return True

def search_students(keyword):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR email LIKE ?
    """, ('%' + keyword + '%', '%' + keyword + '%'))

    students = cursor.fetchall()

    connection.close()

    return students

def delete_book(book_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM issued_books
        WHERE book_id = ?
    """, (book_id,))

    issue_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM reservations
        WHERE book_id = ?
    """, (book_id,))

    reservation_count = cursor.fetchone()[0]

    if issue_count > 0 or reservation_count > 0:
        connection.close()
        return False

    cursor.execute(
        "DELETE FROM books WHERE book_id = ?",
        (book_id,)
    )

    connection.commit()
    connection.close()

    return True


# 8. Create tables when this file is imported or run
create_tables()

print("ShelfWise database created successfully!")
