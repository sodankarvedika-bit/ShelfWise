
import streamlit as st
import pandas as pd
from datetime import date, timedelta

from database import (
    add_book,
    get_books,
    search_books,
    update_book,
    delete_book,
    create_tables,
    add_student,
    get_students,
    search_students,
    issue_book,
    get_active_issues,
    return_book,
    calculate_fine,
    add_reservation,
    get_reservations,
    cancel_reservation
)

# -------------------------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="ShelfWise Library Management",
    page_icon="📚",
    layout="wide"
)

create_tables()

# -------------------------------------------------
# 2. SIDEBAR NAVIGATION
# -------------------------------------------------

st.sidebar.title("📚 ShelfWise")
st.sidebar.write("Library Management System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Book Management",
        "Student Management",
        "Issue & Return",
        "Fine Calculation",
        "Reservations",
        "ShelfBot AI",
        "Book Recommendations",
        "Reports"
    ]
)

# -------------------------------------------------
# 3. DASHBOARD
# -------------------------------------------------

if menu == "Dashboard":

    st.title("📚 ShelfWise Dashboard")

    st.write(
        "Welcome to ShelfWise - Your Smart Library Management System."
    )

    books = get_books()
    students = get_students()
    active_issues = get_active_issues()

    total_books = sum(book[4] for book in books)
    available_books = sum(book[5] for book in books)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Book Copies", total_books)
    col2.metric("Available Copies", available_books)
    col3.metric("Registered Students", len(students))
    col4.metric("Currently Issued", len(active_issues))

    st.divider()
    st.subheader("📖 Book Collection")

    if books:

        book_data = []

        for book in books:
            book_data.append({
                "Book ID": book[0],
                "Title": book[1],
                "Author": book[2],
                "Category": book[3],
                "Quantity": book[4],
                "Available": book[5]
            })

        st.dataframe(
            pd.DataFrame(book_data),
            use_container_width=True
        )

    else:
        st.info("No books have been added yet.")

# -------------------------------------------------
# 4. BOOK MANAGEMENT
# -------------------------------------------------

elif menu == "Book Management":

    st.title("📚 Book Management")

    # ADD BOOK

    st.subheader("➕ Add New Book")

    with st.form("add_book_form"):

        title = st.text_input("Book Title")
        author = st.text_input("Author")
        category = st.text_input("Category")

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1
        )

        add_button = st.form_submit_button("Add Book")

    if add_button:

        if title.strip() and author.strip():

            add_book(
                title.strip(),
                author.strip(),
                category.strip(),
                int(quantity)
            )

            st.success("Book added successfully!")
            st.rerun()

        else:
            st.error("Please enter the book title and author.")

    st.divider()

    # SEARCH BOOK

    st.subheader("🔍 Search Books")

    keyword = st.text_input(
        "Enter book title or author",
        key="book_search"
    )

    if st.button("Search Books"):

        results = search_books(keyword.strip())

        if results:

            search_data = []

            for book in results:
                search_data.append({
                    "Book ID": book[0],
                    "Title": book[1],
                    "Author": book[2],
                    "Category": book[3],
                    "Quantity": book[4],
                    "Available": book[5]
                })

            st.dataframe(
                pd.DataFrame(search_data),
                use_container_width=True
            )

        else:
            st.warning("No matching books found.")

    st.divider()

    # DISPLAY ALL BOOKS

    st.subheader("📖 All Books")

    books = get_books()

    if books:

        book_data = []

        for book in books:
            book_data.append({
                "Book ID": book[0],
                "Title": book[1],
                "Author": book[2],
                "Category": book[3],
                "Quantity": book[4],
                "Available": book[5]
            })

        st.dataframe(
            pd.DataFrame(book_data),
            use_container_width=True
        )

    else:
        st.info("No books available.")

    st.divider()

    # UPDATE BOOK

    st.subheader("✏️ Update Book Details")

    if books:

        selected_book_id = st.selectbox(
            "Select Book ID to Update",
            [book[0] for book in books],
            key="update_book_id"
        )

        # IMPORTANT: Define selected_book before using it.

        selected_book = next(
            (
                book for book in books
                if book[0] == selected_book_id
            ),
            None
        )

        if selected_book is not None:

            with st.form("update_book_form"):

                new_title = st.text_input(
                    "Book Title",
                    value=str(selected_book[1] or "")
                )

                new_author = st.text_input(
                    "Author",
                    value=str(selected_book[2] or "")
                )

                new_category = st.text_input(
                    "Category",
                    value=str(selected_book[3] or "")
                )

                new_quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=max(1, int(selected_book[4])),
                    step=1
                )

                update_button = st.form_submit_button(
                    "Update Book"
                )

            if update_button:

                if new_title.strip() and new_author.strip():

                    success = update_book(
                        selected_book_id,
                        new_title.strip(),
                        new_author.strip(),
                        new_category.strip(),
                        int(new_quantity)
                    )

                    if success:
                        st.success("Book details updated successfully!")
                        st.rerun()

                    else:
                        st.error(
                            "Unable to update. Check whether the quantity "
                            "is less than the number of copies issued."
                        )

                else:
                    st.error("Title and author cannot be empty.")

    else:
        st.info("Add a book before updating.")

    st.divider()

    # DELETE BOOK

    st.subheader("🗑️ Delete Book")

    if books:

        delete_book_id = st.selectbox(
            "Select Book ID to Delete",
            [book[0] for book in books],
            key="delete_book_id"
        )

        if st.button("Delete Selected Book"):

            success = delete_book(delete_book_id)

            if success:
                st.success("Book deleted successfully!")
                st.rerun()

            else:
                st.error(
                    "This book has issue or reservation records "
                    "and cannot be deleted."
                )

    else:
        st.info("No books available to delete.")

# -------------------------------------------------
# 5. STUDENT MANAGEMENT
# -------------------------------------------------

elif menu == "Student Management":

    st.title("👨‍🎓 Student Management")

    st.subheader("➕ Register New Student")

    with st.form("student_form"):

        name = st.text_input("Student Name")
        email = st.text_input("Email Address")
        department = st.text_input("Department")

        register_button = st.form_submit_button(
            "Register Student"
        )

    if register_button:

        if name.strip() and email.strip():

            success = add_student(
                name.strip(),
                email.strip(),
                department.strip()
            )

            if success:
                st.success("Student registered successfully!")
                st.rerun()

            else:
                st.error("This email is already registered.")

        else:
            st.error("Please enter the student name and email.")

    st.divider()

    st.subheader("🔍 Search Students")

    student_keyword = st.text_input(
        "Enter student name or email",
        key="student_search"
    )

    if st.button("Search Students"):

        results = search_students(student_keyword.strip())

        if results:

            student_data = []

            for student in results:
                student_data.append({
                    "Student ID": student[0],
                    "Name": student[1],
                    "Email": student[2],
                    "Department": student[3]
                })

            st.dataframe(
                pd.DataFrame(student_data),
                use_container_width=True
            )

        else:
            st.warning("No matching students found.")

    st.divider()

    st.subheader("📋 Registered Students")

    students = get_students()

    if students:

        student_data = []

        for student in students:
            student_data.append({
                "Student ID": student[0],
                "Name": student[1],
                "Email": student[2],
                "Department": student[3]
            })

        st.dataframe(
            pd.DataFrame(student_data),
            use_container_width=True
        )

    else:
        st.info("No students registered yet.")

# -------------------------------------------------
# 6. ISSUE AND RETURN BOOKS
# -------------------------------------------------

elif menu == "Issue & Return":

    st.title("📕 Issue & Return Books")

    books = get_books()
    students = get_students()

    available_book_list = [
        book for book in books if book[5] > 0
    ]

    st.subheader("📤 Issue a Book")

    if students and available_book_list:

        student_options = {
            f"{student[1]} (ID: {student[0]})": student[0]
            for student in students
        }

        book_options = {
            f"{book[1]} (Available: {book[5]})": book[0]
            for book in available_book_list
        }

        with st.form("issue_book_form"):

            selected_student = st.selectbox(
                "Select Student",
                list(student_options.keys())
            )

            selected_book = st.selectbox(
                "Select Available Book",
                list(book_options.keys())
            )

            issue_date = st.date_input(
                "Issue Date",
                value=date.today()
            )

            due_date = st.date_input(
                "Due Date",
                value=date.today() + timedelta(days=14),
                min_value=issue_date
            )

            issue_button = st.form_submit_button(
                "Issue Book"
            )

        if issue_button:

            success = issue_book(
                student_options[selected_student],
                book_options[selected_book],
                issue_date.isoformat(),
                due_date.isoformat()
            )

            if success:
                st.success("Book issued successfully!")
                st.rerun()

            else:
                st.error("Unable to issue this book.")

    else:
        st.info(
            "Please register at least one student and add an "
            "available book before issuing."
        )

    st.divider()

    st.subheader("📋 Currently Issued Books")

    active_issues = get_active_issues()

    if active_issues:

        issue_data = []

        for item in active_issues:
            issue_data.append({
                "Issue ID": item[0],
                "Student Name": item[1],
                "Book Title": item[2],
                "Issue Date": item[3],
                "Due Date": item[4]
            })

        st.dataframe(
            pd.DataFrame(issue_data),
            use_container_width=True
        )

    else:
        st.info("No books are currently issued.")

    st.divider()

    st.subheader("📥 Return a Book")

    if active_issues:

        issue_options = {
            f"Issue ID: {item[0]} - {item[1]} - {item[2]}": item[0]
            for item in active_issues
        }

        with st.form("return_book_form"):

            selected_issue = st.selectbox(
                "Select Issued Book",
                list(issue_options.keys())
            )

            return_date = st.date_input(
                "Return Date",
                value=date.today()
            )

            return_button = st.form_submit_button(
                "Return Book"
            )

        if return_button:

            success = return_book(
                issue_options[selected_issue],
                return_date.isoformat()
            )

            if success:
                st.success("Book returned successfully!")
                st.rerun()

            else:
                st.error("Unable to return this book.")

    else:
        st.info("There are no issued books to return.")

# -------------------------------------------------
# 7. FINE CALCULATION
# -------------------------------------------------

elif menu == "Fine Calculation":

    st.title("💰 Fine Calculation")

    st.write("Check overdue books and calculate student fines.")

    st.divider()

    st.subheader("📋 Overdue Book Details")

    active_issues = get_active_issues()

    fine_records = []
    total_fine = 0

    if active_issues:

        for item in active_issues:

            issue_id = item[0]
            student_name = item[1]
            book_title = item[2]
            due_date = item[4]

            late_days, fine = calculate_fine(due_date)

            if late_days > 0:

                fine_records.append({
                    "Issue ID": issue_id,
                    "Student Name": student_name,
                    "Book Title": book_title,
                    "Due Date": due_date,
                    "Late Days": late_days,
                    "Fine (₹)": fine
                })

                total_fine += fine

        col1, col2 = st.columns(2)

        col1.metric(
            "Overdue Books",
            len(fine_records)
        )

        col2.metric(
            "Total Outstanding Fine",
            f"₹{total_fine}"
        )

        st.divider()

        if fine_records:

            st.dataframe(
                pd.DataFrame(fine_records),
                use_container_width=True
            )

        else:
            st.success("Great! There are no overdue books currently.")

    else:
        st.info(
            "No books are currently issued. "
            "Issue a book first to calculate fines."
        )

    st.divider()

    st.subheader("ℹ️ Fine Rules")

    st.write("Fine per day: ₹5")

    st.write(
        "Fine is calculated only when a book is overdue. "
        "The current outstanding fine is calculated up to today's date."
    )

# -------------------------------------------------
# 8. RESERVATIONS
# -------------------------------------------------

elif menu == "Reservations":

    st.title("📅 Book Reservations")

    st.write(
        "Students can reserve books that are currently unavailable."
    )

    st.divider()

    books = get_books()
    students = get_students()

    unavailable_books = [
        book for book in books if book[5] == 0
    ]

    st.subheader("➕ Reserve a Book")

    if students and unavailable_books:

        student_options = {
            f"{student[1]} (ID: {student[0]})": student[0]
            for student in students
        }

        book_options = {
            f"{book[1]} (ID: {book[0]})": book[0]
            for book in unavailable_books
        }

        with st.form("reservation_form"):

            selected_student = st.selectbox(
                "Select Student",
                list(student_options.keys())
            )

            selected_book = st.selectbox(
                "Select Unavailable Book",
                list(book_options.keys())
            )

            reservation_date = st.date_input(
                "Reservation Date",
                value=date.today()
            )

            reserve_button = st.form_submit_button(
                "Reserve Book"
            )

        if reserve_button:

            success = add_reservation(
                student_options[selected_student],
                book_options[selected_book],
                reservation_date.isoformat()
            )

            if success:
                st.success("Book reserved successfully!")
                st.rerun()

            else:
                st.error("Unable to reserve this book.")

    elif not students:

        st.warning(
            "Please register a student before making a reservation."
        )

    else:

        st.info(
            "There are no unavailable books to reserve currently. "
            "Issue all copies of a book to test reservations."
        )

    st.divider()

    st.subheader("📋 All Reservations")

    reservations = get_reservations()

    if reservations:

        reservation_data = []

        for item in reservations:
            reservation_data.append({
                "Reservation ID": item[0],
                "Student Name": item[1],
                "Book Title": item[2],
                "Reservation Date": item[3],
                "Status": item[4]
            })

        st.dataframe(
            pd.DataFrame(reservation_data),
            use_container_width=True
        )

    else:
        st.info("No reservations have been made yet.")

    st.divider()

    st.subheader("❌ Cancel Reservation")

    pending_reservations = [
        item for item in reservations
        if item[4] == "Pending"
    ]

    if pending_reservations:

        reservation_options = {
            f"Reservation {item[0]} - {item[1]} - {item[2]}": item[0]
            for item in pending_reservations
        }

        selected_reservation = st.selectbox(
            "Select Reservation",
            list(reservation_options.keys())
        )

        if st.button("Cancel Selected Reservation"):

            success = cancel_reservation(
                reservation_options[selected_reservation]
            )

            if success:
                st.success("Reservation cancelled successfully!")
                st.rerun()

            else:
                st.error("Unable to cancel reservation.")

    else:
        st.info("There are no pending reservations to cancel.")

# -------------------------------------------------
# 9. SHELFBOT AI CHATBOT
# -------------------------------------------------


elif menu == "ShelfBot AI":


    st.title("🤖 ShelfBot AI - Smart Library Assistant")
    
    # Initialize chatbot conversation history

    if "shelfbot_messages" not in st.session_state:
        st.session_state["shelfbot_messages"] = []

    st.write(
        "Hello! I am ShelfBot Version 2. "
        "I can help you search books, check availability, "
        "find recommendations and understand library services."
    )

    st.divider()

    # -----------------------------------------
    # CHATBOT RESPONSE FUNCTION
    # -----------------------------------------

    def chatbot_response(question):

        books = get_books()

        question = question.lower().strip()
        words = [
            word.strip(".,?!:;()")
            for word in question.split()
        ]

        # Words that should not be used for book matching
        stop_words = {
            "show", "me", "find", "search", "book", "books",
            "the", "a", "an", "is", "are", "do", "does",
            "you", "have", "any", "on", "in", "for", "of",
            "please", "tell", "what", "which", "can", "i",
            "some", "about", "by", "give", "recommend",
            "suggest", "available", "want", "need", "to"
        }

        keywords = [
            word for word in words
            if word and word not in stop_words
        ]
        
        # -------------------------------------
        # SMART KEYWORD RECOGNITION
        # -------------------------------------

        if "ai" in words:
            keywords.extend(["artificial", "intelligence"])

        if "ml" in words:
            keywords.extend(["machine", "learning"])

        if "coding" in words:
            keywords.append("programming")

        if "novel" in words or "novels" in words:
            keywords.append("fiction")

        if "stories" in words:
            keywords.append("fiction")

        if "money" in words:
            keywords.append("finance")

        if "technology" in words:
            keywords.append("computer")


        # -------------------------------------
        # 1. GREETING
        # -------------------------------------

        if any(word in words for word in ["hello", "hi", "hey", "hii"]):

            return (
                "Hello! Welcome to ShelfWise Library! 😊\n\n"
                "I am ShelfBot. How can I help you today?"
            )
                # -------------------------------------
        # SIMILAR BOOK SUGGESTIONS
        # -------------------------------------

        elif any(word in words for word in ["similar", "related", "alike"]):

            previous_books = st.session_state["shelfbot_last_books"]

            if not previous_books:
                return "Please search for a book first. Then I can suggest similar books."

            reference_book = previous_books[0]

            reference_category = str(
                reference_book[3] or ""
            ).strip().lower()

            if not reference_category:
                return "This book does not have a category. Please try another book."

            similar_books = [
                book for book in books
                if book[0] != reference_book[0]
                and book[5] > 0
                and str(book[3] or "").strip().lower() == reference_category
            ]

            if not similar_books:
                return "Sorry! I couldn't find other available books in this category."

            response = (
                f"⭐ Books similar to {reference_book[1]}:\n\n"
                f"Category: {reference_category.title()}\n\n"
            )

            for book in similar_books[:5]:
                response += (
                    f"📖 {book[1]}\n"
                    f"Author: {book[2]}\n"
                    f"Available Copies: {book[5]}\n\n"
                )

            return response
        
        # -------------------------------------
        # VERSION 5: AUTHOR-BASED SEARCH
        # -------------------------------------

        elif (
            "who is the author" in question
            or "author of this book" in question
            or "who wrote this book" in question
            or "books by this author" in question
            or "other books by this author" in question
            or "more books by this author" in question
        ):

            previous_books = st.session_state["shelfbot_last_books"]

            if not previous_books:
                return "Please search for a book first."

            reference_book = previous_books[0]
            author_name = str(reference_book[2]).strip()

            if not author_name:
                return "Sorry! The author information is not available."

            author_books = [
                book for book in books
                if str(book[2]).strip().lower() == author_name.lower()
                and book[0] != reference_book[0]
                and book[5] > 0
            ]

            response = (
                f"✍️ Author Information\n\n"
                f"📖 Book: {reference_book[1]}\n"
                f"👤 Author: {author_name}\n\n"
            )

            if author_books:

                response += "📚 Other available books by this author:\n\n"

                for book in author_books[:5]:
                    response += (
                        f"📖 {book[1]}\n"
                        f"Category: {book[3]}\n"
                        f"Available Copies: {book[5]}\n\n"
                    )

            else:
                response += (
                    "No other available books by this author "
                    "were found in the library."
                )

            return response
        
        # -------------------------------------
        # VERSION 6: BOOK DETAILS ASSISTANT
        # -------------------------------------

        
        elif (
            "details" in question
            or "more about this book" in question
            or "tell me about this book" in question
            or "category of this book" in question
            or "what category does this book belong to" in question
            or "total quantity" in question
            or "how many copies" in question
            or "how many copies are available" in question
            or "book information" in question
        ):


            previous_books = st.session_state["shelfbot_last_books"]

            if not previous_books:
                return "Please search for a book first."

            book = previous_books[0]

            total_quantity = book[4]
            available_quantity = book[5]
            issued_quantity = total_quantity - available_quantity

            return (
                "📚 COMPLETE BOOK DETAILS\n\n"
                f"📖 Book Title: {book[1]}\n\n"
                f"✍️ Author: {book[2]}\n\n"
                f"📂 Category: {book[3]}\n\n"
                f"📚 Total Quantity: {total_quantity}\n\n"
                f"✅ Available Copies: {available_quantity}\n\n"
                f"📤 Issued Copies: {issued_quantity}\n\n"
                "Hope this information helps you! 😊"
            )
        
        
        elif (
            "library activity report" in question
            or "student activity report" in question
            or "activity report for" in question
            or "student report" in question
        ):
            students = get_students()
            issues = get_active_issues()

            student_name = question.lower().strip()

            search_phrases = [
                "give me",
                "show me",
                "generate",
                "library activity report",
                "student activity report",
                "activity report for",
                "student report for",
                "student report",
                "report for",
                "report"
            ]

            for phrase in search_phrases:
                student_name = student_name.replace(phrase, "")

            student_name = student_name.replace("'s", "")
            student_name = student_name.replace("’s", "")
            student_name = student_name.strip(" ?.,!")

            found_student = None

            for student in students:
                full_name = str(student[1]).strip().lower()

                if (
                    student_name == full_name
                    or student_name == full_name.split()[0]
                ):
                    found_student = student
                    break

            if not found_student:
                return "Sorry! I couldn't find this student."

            student_issues = [
                issue for issue in issues
                if str(issue[1]).strip().lower()
                == str(found_student[1]).strip().lower()
            ]

            total_fine = 0

            response = (
                "📊 STUDENT LIBRARY ACTIVITY REPORT\n\n"
                f"👤 Name: {found_student[1]}\n"
                f"📧 Email: {found_student[2]}\n"
                f"🏫 Department: {found_student[3]}\n\n"
                "📚 BOOK ACTIVITY\n\n"
                f"Total Currently Issued Books: {len(student_issues)}\n\n"
            )

            if student_issues:
                for issue in student_issues:
                    late_days, fine = calculate_fine(issue[4])

                    total_fine += fine

                    response += (
                        f"📖 Book: {issue[2]}\n"
                        f"📅 Issue Date: {issue[3]}\n"
                        f"⏰ Due Date: {issue[4]}\n"
                        f"⚠️ Late Days: {late_days}\n"
                        f"💰 Fine: ₹{fine}\n\n"
                    )
            else:
                response += "No currently issued books.\n\n"

            response += (
                "💰 TOTAL OVERDUE FINE\n"
                f"₹{total_fine}\n\n"
                "Report generated successfully! 😊"
            )

            return response

        elif (
            "find student" in question
            or "search student" in question
            or "student details" in question
            or "student information" in question
            or "student profile" in question
        ):
            students = get_students()

            search_name = question

            
            search_phrases = [
                "what is the overdue fine for",
                "what is the fine for",
                "calculate fine for",
                "overdue fine for",
                "how much fine does",
                "how much fine do",
                "fine does",
                "fine for",
                "owe",
                "owes"
            ]


            for phrase in search_phrases:
                search_name = search_name.replace(phrase, "")

            search_name = search_name.strip()

            found_student = None

            for student in students:
                student_name = str(student[1]).strip().lower()

                if (
                    search_name == student_name
                    or search_name == student_name.split()[0]
                ):
                    found_student = student
                    break

            if found_student:
                return (
                    "🎓 STUDENT INFORMATION\n\n"
                    f"👤 Name: {found_student[1]}\n\n"
                    f"📧 Email: {found_student[2]}\n\n"
                    f"🏫 Department: {found_student[3]}\n\n"
                    "Student record found successfully! 😊"
                )

            else:
                return (
                    "Sorry! I couldn't find this student.\n\n"
                    "Please check the student's name and try again."
                )
        
        elif (
            "pending returns" in question
            or "need to return" in question
            or "books to return" in question
            or "pending books" in question
            or "active book issues" in question
        ):
            issues = get_active_issues()

            student_name = question.lower().strip()

            search_phrases = [
                "show pending returns for",
                "pending returns for",
                "show pending returns",
                "pending returns",
                "which books does",
                "which books has",
                "need to return",
                "books to return",
                "pending books for",
                "pending books",
                "active book issues for",
                "active book issues"
            ]

            for phrase in search_phrases:
                student_name = student_name.replace(phrase, "")

            student_name = student_name.replace("what is", "")
            student_name = student_name.replace("the", "")
            student_name = student_name.replace("-", "")
            student_name = student_name.strip(" ?.,!-")

            matching_issues = [
                issue for issue in issues
                if student_name in str(issue[1]).lower()
            ]

            if matching_issues:
                response = (
                    f"📚 PENDING RETURNS FOR "
                    f"{matching_issues[0][1]}:\n\n"
                )

                for issue in matching_issues:
                    response += (
                        f"📖 Book: {issue[2]}\n"
                        f"📅 Issue Date: {issue[3]}\n"
                        f"⏰ Due Date: {issue[4]}\n\n"
                    )

                return response

            else:
                return (
                    f"✅ No pending book returns found for "
                    f"{student_name.title()}."
                )
        
        elif (
            "books issued by" in question
            or "books borrowed by" in question
            or "which books has" in question
            or "show books borrowed" in question
            or "issued by" in question
        ):
            issues = get_active_issues()

            
            student_name = question.lower().strip()

            search_phrases = [
                "which books has",
                "which books have",
                "books issued by",
                "books borrowed by",
                "show books borrowed by",
                "show books borrowed",
                "issued by",
                "issued"
            ]

            for phrase in search_phrases:
                student_name = student_name.replace(phrase, "")

            student_name = student_name.strip(" ?.,!")


            matching_issues = [
                issue for issue in issues
                if student_name.lower() in str(issue[1]).lower()
            ]

            if matching_issues:
                response = (
                    f"📚 Books issued by {matching_issues[0][1]}:\n\n"
                )

                for issue in matching_issues:
                    response += (
                        f"📖 Book: {issue[2]}\n"
                        f"📅 Issue Date: {issue[3]}\n"
                        f"⏰ Due Date: {issue[4]}\n\n"
                    )

                return response

            else:
                return (
                    f"No active issued books found for "
                    f"{student_name.title()}."
                )

        
        elif (
            "overdue fine for" in question
            or "fine for" in question
            or "calculate fine for" in question
            or "how much fine does" in question
            or "fine does" in question
        ):
            issues = get_active_issues()

            student_name = question.lower().strip()

            
            search_phrases = [
                "what is the overdue fine for",
                "what is the fine for",
                "calculate fine for",
                "overdue fine for",
                "how much fine does",
                "fine does",
                "fine for",
                "owe"
            ]


            for phrase in search_phrases:
                student_name = student_name.replace(phrase, "")

            student_name = student_name.replace("what is", "")
            student_name = student_name.replace("the", "")
            student_name = student_name.strip(" ?.,!")

            matching_issues = [
                issue for issue in issues
                if student_name in str(issue[1]).lower()
            ]

            if not matching_issues:
                return (
                    f"No active book issues found for "
                    f"{student_name.title()}."
                )

            response = (
                f"💰 OVERDUE FINE DETAILS\n"
                f"Student: {matching_issues[0][1]}\n\n"
            )

            total_fine = 0

            for issue in matching_issues:
                due_date = issue[4]

                late_days, fine = calculate_fine(due_date)

                if late_days > 0:
                    response += (
                        f"📖 Book: {issue[2]}\n"
                        f"⏰ Due Date: {due_date}\n"
                        f"⚠️ Late Days: {late_days}\n"
                        f"💰 Fine: ₹{fine}\n\n"
                    )

                    total_fine += fine

            if total_fine == 0:
                return (
                    f"✅ {matching_issues[0][1]} has no overdue fine.\n"
                    "All currently issued books are within their due dates."
                )

            response += (
                "--------------------------\n"
                f"💰 Total Outstanding Fine: ₹{total_fine}"
            )

            return response

        # -------------------------------------
        # 2. FINE INFORMATION
        # -------------------------------------

        elif "fine" in question or "penalty" in question:

            return (
                "💰 ShelfWise Fine Information\n\n"
                "The library charges ₹5 per overdue day.\n"
                "The fine is calculated according to the "
                "number of days after the due date."
            )
        
        # -------------------------------------
        # LIBRARY STATISTICS
        # -------------------------------------

        elif (
            "statistics" in question
            or "summary" in question
            or "library status" in question
            or "how many books" in question
            or "how many students" in question
        ):

            students = get_students()
            active_issues = get_active_issues()

            total_books = sum(book[4] for book in books)
            available_books = sum(book[5] for book in books)
            issued_books = len(active_issues)

            return (
                "📊 ShelfWise Library Summary\n\n"
                f"📚 Total Book Copies: {total_books}\n\n"
                f"✅ Available Copies: {available_books}\n\n"
                f"📤 Currently Issued: {issued_books}\n\n"
                f"👨‍🎓 Registered Students: {len(students)}\n\n"
                "I hope this summary helps you!"
            )


        # -------------------------------------
        # 3. LIBRARY TIMINGS
        # -------------------------------------

        elif (
            "timing" in question
            or "hours" in question
            or "opening time" in question
            or "closing time" in question
        ):

            return (
                "🕒 Please contact your library staff "
                "to know the official opening and closing timings."
            )

        # -------------------------------------
        # 4. ISSUE BOOK INFORMATION
        # -------------------------------------

        elif "issue" in question:

            return (
                "📤 How to Issue a Book:\n\n"
                "1. Open Issue & Return.\n"
                "2. Select the student.\n"
                "3. Select an available book.\n"
                "4. Choose the issue date and due date.\n"
                "5. Click Issue Book.\n\n"
                "The book will be added to active issues."
            )

        # -------------------------------------
        # 5. RETURN BOOK INFORMATION
        # -------------------------------------

        elif "return" in question:

            return (
                "📥 How to Return a Book:\n\n"
                "1. Open Issue & Return.\n"
                "2. Find the currently issued book.\n"
                "3. Select the issue record.\n"
                "4. Enter the return date.\n"
                "5. Click Return Book.\n\n"
                "The available book count will be updated."
            )

        # -------------------------------------
        # 6. RESERVATION INFORMATION
        # -------------------------------------

        elif "reservation" in question or "reserve" in question:

            return (
                "📅 How to Reserve a Book:\n\n"
                "1. Open Reservations.\n"
                "2. Select a registered student.\n"
                "3. Select an unavailable book.\n"
                "4. Choose the reservation date.\n"
                "5. Click Reserve Book."
            )

        # -------------------------------------
        # 7. SHOW ALL BOOKS
        # -------------------------------------

        elif (
            "all books" in question
            or "list books" in question
            or "book collection" in question
        ):

            if not books:
                return "There are no books in the library yet."

            response = "📚 Books in ShelfWise Library:\n\n"

            for book in books:

                response += (
                    f"📖 {book[1]}\n"
                    f"Author: {book[2]}\n"
                    f"Category: {book[3]}\n"
                    f"Available Copies: {book[5]}\n\n"
                )

            return response

        # -------------------------------------
        # 8. SHOW AVAILABLE BOOKS
        # -------------------------------------
                # -------------------------------------
        # FOLLOW-UP QUESTION: CHECK PREVIOUS BOOKS
        # -------------------------------------

        elif (
            "available" in question
            and any(word in words for word in ["these", "them", "those"])
        ):

            previous_books = st.session_state["shelfbot_last_books"]

            if not previous_books:
                return "Please search for some books first."

            available_previous = [
                book for book in previous_books if book[5] > 0
            ]

            if not available_previous:
                return "Sorry! None of those previously found books are available."

            response = "✅ Available books from your previous search:\n\n"

            for book in available_previous:
                response += (
                    f"📖 {book[1]} by {book[2]}\n"
                    f"Available Copies: {book[5]}\n\n"
                )

            return response
        elif "available" in question:

            available_books = [
                book for book in books if book[5] > 0
            ]

            if not available_books:
                return "Sorry! No books are currently available."

            response = "✅ Available Books:\n\n"

            for book in available_books:

                response += (
                    f"📖 {book[1]} by {book[2]}\n"
                    f"Available Copies: {book[5]}\n\n"
                )

            return response

        # -------------------------------------
        # 9. SMART RECOMMENDATIONS
        # -------------------------------------

        elif "recommend" in question or "suggest" in question:

            available_books = [
                book for book in books if book[5] > 0
            ]

            if not available_books:
                return "There are no available books to recommend."

            matching_books = []

            for book in available_books:

                title = str(book[1]).lower()
                author = str(book[2]).lower()
                category = str(book[3] or "").lower()

                score = 0

                for word in keywords:

                    if word in title:
                        score += 3

                    if word in author:
                        score += 2

                    if word in category:
                        score += 3

                if score > 0:
                    matching_books.append((score, book))

            matching_books.sort(
                key=lambda item: item[0],
                reverse=True
            )

            if matching_books:

                response = "⭐ My Book Recommendations:\n\n"

                for score, book in matching_books[:5]:

                    response += (
                        f"📖 {book[1]}\n"
                        f"Author: {book[2]}\n"
                        f"Category: {book[3]}\n"
                        f"Available Copies: {book[5]}\n\n"
                    )

                return response

            categories = sorted(set(
                str(book[3]).strip()
                for book in available_books
                if book[3] and str(book[3]).strip()
            ))

            if categories:

                return (
                    "Please mention a topic or category "
                    "so I can suggest suitable books.\n\n"
                    "Available categories: "
                    + ", ".join(categories)
                )

            return "Please add book categories to get recommendations."

        # -------------------------------------
        # 10. SMART BOOK SEARCH
        # -------------------------------------

        matching_books = []

        for book in books:

            title = str(book[1]).lower()
            author = str(book[2]).lower()
            category = str(book[3] or "").lower()

            score = 0

            for word in keywords:

                if word in title:
                    score += 3

                if word in author:
                    score += 2

                if word in category:
                    score += 2

            if score > 0:
                matching_books.append((score, book))

        matching_books.sort(
            key=lambda item: item[0],
            reverse=True
        )
        st.session_state["shelfbot_last_books"] = [
            book for score, book in matching_books[:10]
        ]

        if matching_books:

            response = "🔍 I found these matching books:\n\n"

            for score, book in matching_books[:10]:

                response += (
                    f"📖 {book[1]}\n"
                    f"Author: {book[2]}\n"
                    f"Category: {book[3]}\n"
                    f"Quantity: {book[4]}\n"
                    f"Available Copies: {book[5]}\n\n"
                )

            return response

        # -------------------------------------
        # 11. DEFAULT RESPONSE
        # -------------------------------------

        return (
            "Sorry! I could not find a matching answer. 😊\n\n"
            "You can ask me questions like:\n\n"
            "1. Show all books\n"
            "2. Show available books\n"
            "3. Find Python books\n"
            "4. Search books by an author\n"
            "5. Recommend AI books\n"
            "6. What is the library fine?\n"
            "7. How do I issue a book?\n"
            "8. How do I return a book?\n"
            "9. How can I reserve a book?"
        )

    # -----------------------------------------
    
    # -----------------------------------------
    # CHAT HISTORY
    # -----------------------------------------

    if "shelfbot_messages" not in st.session_state:
        st.session_state["shelfbot_messages"] = []

    for message in st.session_state["shelfbot_messages"]:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    st.divider()

    # -----------------------------------------
    # QUICK QUESTION BUTTONS
    # -----------------------------------------

    st.subheader("💡 Quick Questions")

    col1, col2, col3 = st.columns(3)

    quick_question = None

    if col1.button("📚 Show All Books"):
        quick_question = "Show all books"

    if col2.button("✅ Available Books"):
        quick_question = "Show available books"

    if col3.button("⭐ Recommend Books"):
        quick_question = "Recommend some books"

    col4, col5 = st.columns(2)

    if col4.button("💰 Fine Information"):
        quick_question = "What is the library fine?"

    if col5.button("📅 Reservation Help"):
        quick_question = "How can I reserve a book?"

    st.divider()

    # -----------------------------------------
    # CHAT INPUT
    # -----------------------------------------

    user_question = st.chat_input(
        "Ask ShelfBot anything about your library..."
    )

    # -----------------------------------------
    # PROCESS USER QUESTION
    # -----------------------------------------

    question_to_process = user_question or quick_question

    if question_to_process:

        st.session_state["shelfbot_messages"].append({
            "role": "user",
            "content": question_to_process
        })

        answer = chatbot_response(question_to_process)

        st.session_state["shelfbot_messages"].append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

    # -----------------------------------------
    # CLEAR CHAT
    # -----------------------------------------

    if st.button("🗑️ Clear Chat"):

        st.session_state["shelfbot_messages"] = []

        st.rerun()



# -------------------------------------------------
# 10. BOOK RECOMMENDATION SYSTEM
# -------------------------------------------------

elif menu == "Book Recommendations":

    st.title("⭐ Smart Book Recommendation System")

    st.write(
        "Find books based on your favourite category or interests."
    )

    st.divider()

    books = get_books()

    if books:

        categories = sorted(set(
            str(book[3]).strip()
            for book in books
            if book[3] and str(book[3]).strip()
        ))

        st.subheader("🎯 Tell us what you like")

        selected_category = st.selectbox(
            "Choose your favourite category",
            ["All Categories"] + categories
        )

        interest = st.text_input(
            "Enter a topic or interest",
            placeholder="Example: Python, AI, Machine Learning"
        )

        if st.button("✨ Get Recommendations"):

            recommendations = []

            keywords = interest.lower().split()

            for book in books:

                title = str(book[1]).lower()
                author = str(book[2]).lower()
                category = str(book[3] or "").lower()

                category_match = (
                    selected_category == "All Categories"
                    or category == selected_category.lower()
                )

                score = 0

                if selected_category != "All Categories":
                    score += 3

                for word in keywords:

                    if word in title:
                        score += 3

                    if word in category:
                        score += 3

                    if word in author:
                        score += 1

                interest_match = (
                    not keywords
                    or any(
                        word in title
                        or word in category
                        or word in author
                        for word in keywords
                    )
                )

                if (
                    category_match
                    and interest_match
                    and book[5] > 0
                ):

                    recommendations.append((score, book))

            recommendations.sort(
                key=lambda item: item[0],
                reverse=True
            )

            if recommendations:

                st.success("Here are your recommended books!")

                for score, book in recommendations:

                    with st.container(border=True):

                        st.subheader(f"📖 {book[1]}")

                        st.write("Author:", book[2])
                        st.write("Category:", book[3] or "Uncategorized")
                        st.write("Available Copies:", book[5])
                        st.write("Recommendation Score:", score)

            else:

                st.warning(
                    "No matching available books found. "
                    "Try another category or topic."
                )

    else:

        st.info(
            "Please add books to your library before using recommendations."
        )

# -------------------------------------------------
# 11. REPORTS
# -------------------------------------------------

elif menu == "Reports":

    st.title("📊 Library Reports")

    books = get_books()
            # Remember books from the previous search
    if "shelfbot_last_books" not in st.session_state:
            st.session_state["shelfbot_last_books"] = []
    students = get_students()
    active_issues = get_active_issues()

    total_books = sum(book[4] for book in books)
    available_books = sum(book[5] for book in books)
    issued_copies = len(active_issues)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Book Copies", total_books)
    col2.metric("Available Copies", available_books)
    col3.metric("Active Issues", issued_copies)

    st.divider()

    st.subheader("📚 Books by Category")

    if books:

        category_data = []

        for book in books:
            category_data.append({
                "Category": book[3] or "Uncategorized",
                "Quantity": book[4]
            })

        category_df = pd.DataFrame(category_data)

        category_summary = (
            category_df.groupby("Category")["Quantity"]
            .sum()
            .reset_index()
        )

        st.bar_chart(
            category_summary.set_index("Category")
        )

    else:
        st.info("Add books to view category reports.")

    st.divider()

    st.subheader("👨‍🎓 Student Summary")

    st.write("Total Registered Students:", len(students))

    st.write("Total Books Currently Issued:", issued_copies)

    st.success("Library report generated successfully.")
