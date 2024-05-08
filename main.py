import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Database connection
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="adeelshah2001",
        database="library"
    )
    if connection.is_connected():
        print("Connected to the database")
except Error as e:
    print(f"Error: {e}")

# Streamlit App
st.title("Library Management System")
selected_option = st.sidebar.selectbox("Select Option",
                                       ["Home", "Add Book", "View Books", "Search Books", "Borrow Book", "Return Book",
                                        "Borrowers List", "User Registration","Registered Users"], key="select_option")

db_config = {"host": "localhost",
             "user": "root",
             "password": "adeelshah2001",
             "database": "library"}

# Function to execute MySQL queries
def fetch_genres():
    query = "SELECT * FROM Genres"
    return execute_query(query)


def fetch_publishers():
    query = "SELECT * FROM Publishers"
    return execute_query(query)


def execute_query2(query, values=None):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execute the query with optional values
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        # Commit the transaction
        conn.commit()

        # Close cursor and connection
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print("MySQL Error:", e)
        return None


def execute_query(query, values=None):
    try:
        cursor = connection.cursor(dictionary=True)
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        connection.commit()
        return result
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()



# Function to add a new book to the database #
def add_book(title, author, genre_id, publisher_id):
    # Establish a connection to the database
    connection = execute_query(query, values)

    try:
        with connection.cursor() as cursor:
            # SQL statement to insert a new book into the Books table
            sql = "INSERT INTO Books (Title, Author, GenreID, PublisherID) VALUES (%s, %s, %s, %s)"
            # Execute the SQL statement with the provided parameters
            cursor.execute(sql, (title, author, genre_id, publisher_id))
        # Commit the transaction
        connection.commit()
    except Exception as e:
        # Handle any errors that occur during the database operation
        print(f"Error adding book: {e}")
    finally:
        # Close the database connection
        connection.close()

def registered_users():
    st.header("Registered Users")
    # SELECT BorrowerID as ID, Name, BookID, Noofbooks as 'No of books' FROM borrowers GROUPBY
    # Query to fetch books data from the database
    query = "SELECT * FROM users"
    # Execute the query and fetch books data
    user = execute_query(query)

    # Check if there are books available in the database
    if user:
        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(user)
        # Display the DataFrame as a table
        st.write(df)
    else:
        st.warning("No Users available")
def login():
    st.title("User Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Validate username and password against database
        query = "SELECT * FROM Users WHERE Username = %s AND Password = %s"
        result = execute_query(query, (username, password))
        if result:
            user_type = result[0]["UserType"]
            if user_type == "Student":
                # admin_panel()
                pass
        else:
            st.error("Invalid username or password")


def user_registration():
    st.title("User Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    query = "INSERT INTO USERS(username,password) VALUES(%s,%s)"
    values = (username, password)
    # user_type = st.selectbox("User Type", ["Librarian", "Student"])
    if st.button("Register"):
        execute_query(query, values)


def view_books():
    ### LEFT JOIN IS USED ###
    query = """
    SELECT b.BookID, b.Title, b.Author, b.Quantity, g.GenreName, p.PublisherName
    FROM Books b
    LEFT JOIN Genres g ON b.GenreID = g.GenreID
    LEFT JOIN Publishers p ON b.PublisherID = p.PublisherID
    """
    books = execute_query(query)

    if books:
        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(books)

        st.write("## Books in Library")
        # Display the DataFrame as a table
        st.write(df)
    else:
        st.warning("No books available in the library.")


# Function to search books with filters
def search_books(title=None, author=None, genre=None, publisher=None):
    query = "SELECT * FROM Books WHERE 1=1"
    params = {}

    if title:
        query += " AND Title LIKE %(title)s"
        params['title'] = f"%{title}%"

    if author:
        query += " AND Author LIKE %(author)s"
        params['author'] = f"%{author}%"

    if genre:
        query += " AND GenreID = %(genre)s"
        params['genre'] = genre['GenreID']

    if publisher:
        query += " AND PublisherID = %(publisher)s"
        params['publisher'] = publisher['PublisherID']

    return execute_query(query, params)

def return_book():
    st.title("Return Book")
    book_id = st.number_input("Enter Book ID to return", min_value=1, step=1)
    borrower_name = st.text_input("Borrower Name:")
    if st.button("Return"):
        # Check if the borrower is registered
        query = "SELECT * FROM Users WHERE Username = %s"
        result1 = execute_query(query, (borrower_name,))
        if not result1:
            st.error("Borrower name is not registered. Please register first.")
        else:
            # Check if the borrower has borrowed the book
            query = "SELECT * FROM Borrowers WHERE Name = %s AND BookID = %s AND Type = 'Borrow'"
            values = (borrower_name, book_id)
            result2 = execute_query(query, values)
            if not result2:
                st.error("You have not borrowed this book.")
            else:
                # query = "UPDATE Borrowers SET Type = 'Return' WHERE BookID = %s AND Name= %s"
                # values = (book_id,)
                # execute_query(query, values)

                query = "UPDATE Transactions SET Type = 'Return' WHERE BookID = %s AND Type = 'Return'"
                values = (book_id,)
                execute_query(query, values)
                # Delete the borrower record for the returned book
                query = "DELETE FROM borrowers WHERE BookID = %s AND Name= %s"
                values = ( book_id,borrower_name,)
                execute_query2(query, values)

                # Update the book quantity
                query = "UPDATE Books SET Quantity = Quantity + 1 WHERE BookID = %s"
                execute_query2(query, (book_id,))

                st.success("Book returned successfully!")

if selected_option == "Home":
    background_image = "books.jpg"
    st.image(background_image, use_column_width=True)
    st.write("21CS Library Management System is a cutting-edge software that modernizes library operations and "
             "enhances the library experience for both librarians and users. Our system offers a wide range of "
             "functionalities aimed at simplifying day-to-day "
             "tasks and improving access to library resources by providing librarians with actionable insights.")
    st.write("Made By:")
    st.write("<ul><li><h5>21CS041</h5></li><li><h5>21CS077</h5></li><li><h5>21CS105</h5></li></ul>",
             unsafe_allow_html=True)

if selected_option == "Search Books":
    st.header("Search Books")

    # Fetch genres and publishers for dropdowns
    genres = fetch_genres()
    publishers = fetch_publishers()

    # Extract genre and publisher names for display
    genre_names = [genre['GenreName'] for genre in genres]
    publisher_names = [publisher['PublisherName'] for publisher in publishers]

    # Add a default option for better user experience
    genre_names.insert(0, "All Genres")
    publisher_names.insert(0, "All Publishers")

    title = st.text_input("Enter Book Title:")
    author = st.text_input("Enter Author:")
    selected_genre = st.selectbox("Select Genre:", genre_names)
    selected_publisher = st.selectbox("Select Publisher:", publisher_names)

    if st.button("Search"):
        # Filter selected genre and publisher
        genre = next((g for g in genres if g['GenreName'] == selected_genre),
                     None) if selected_genre != "All Genres" else None
        publisher = next((p for p in publishers if p['PublisherName'] == selected_publisher),
                         None) if selected_publisher != "All Publishers" else None

        # Perform search with filters
        search_results = search_books(title=title, author=author, genre=genre, publisher=publisher)

        # Display search results
        if search_results:
            st.subheader("Search Results:")
            for book in search_results:
                st.write(
                    f"BookID: {book['BookID']}, Title: {book['Title']}, Author: {book['Author']}, Genre: {selected_genre}, Publisher: {selected_publisher}")
        else:
            st.warning("No books found matching the search criteria.")


elif selected_option == "Add Book":
    st.header("Add a New Book")

    title = st.text_input("Title:")
    author = st.text_input("Author:")
    quantity = st.number_input("Quantity:", min_value=0, step=1)

    genres = fetch_genres()
    publishers = fetch_publishers()

    genre_names = [genre['GenreName'] for genre in genres]
    publisher_names = [publisher['PublisherName'] for publisher in publishers]

    selected_genre = st.selectbox("Select Genre:", genre_names)
    selected_publisher = st.selectbox("Select Publisher:", publisher_names)


    if st.button("Add Book"):
        if selected_genre == "Select Genre" or selected_publisher == "Select Publisher":
            st.error("Please select a valid genre and publisher.")
            print(genre_names)
        else:
            genre = next((g for g in genres if g['GenreName'] == selected_genre), None)
            publisher = next((p for p in publishers if p['PublisherName'] == selected_publisher), None)

            if genre and publisher:
                # Extract GenreID and PublisherID from objects
                genre_id = genre['GenreID']
                publisher_id = publisher['PublisherID']

                query = "INSERT INTO Books (Title, Author, Quantity, GenreID, PublisherID) VALUES (%s, %s, %s, %s, %s)"
                values = (title, author, quantity, genre_id, publisher_id)
                execute_query(query, values)
                st.success("Book added successfully!")
            else:
                st.error("Selected genre or publisher not found. Please try again.")

elif selected_option == "View Books":
    st.header("View Books")

    # Query to fetch books data from the database
    query = """
       SELECT b.BookID, b.Title, b.Author, b.Quantity, g.GenreName, p.PublisherName
       FROM Books b
       LEFT JOIN Genres g ON b.GenreID = g.GenreID
       LEFT JOIN Publishers p ON b.PublisherID = p.PublisherID
       """

    # Execute the query and fetch books data
    books = execute_query(query)

    # Check if there are books available in the database
    if books:
        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(books)

        # Display the DataFrame as a table
        st.write(df)
    else:
        st.warning("No books available in the library.")

elif selected_option == "Borrowers List":
    st.header("Borrowers List")

    query = """
           SELECT Name,Count(Name) as 'No. of books'
           FROM borrowers
           WHERE Type = 'Borrow'
           GROUP BY Name;
           """
    ### NORMALIZATION HERE ### INNER JOIN USED
    query2 ="""
              SELECT Users.UserID, Borrowers.Name, books.Title AS BookName
              FROM Borrowers
              JOIN Users ON Borrowers.Name = Users.Username
              JOIN books ON Borrowers.BookID = books.bookid;
            """

    # Execute the query and fetch books data
    borr = execute_query(query2)

    # Check if there are books available in the database
    if borr:
        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(borr)
        # Display the DataFrame as a table
        st.write(df)
    else:
        st.warning("No one has borrowed a book.")
elif selected_option == "Borrow Book":
    st.header("Borrow a Book")
    borrower_name = st.text_input("Borrower Name:")
    book_id = st.number_input("BookID:", min_value=1, step=1)

    if st.button("Borrow Book"):
        query = "SELECT * FROM Users WHERE Username = %s"
        result1 = execute_query(query, (borrower_name,))
        if not result1:
            st.error("Borrower name is not registered. Please register first.")
        else:
            # Check if the user has borrowed the same book before or not
            query = f"SELECT * FROM borrowers WHERE Name = %s AND BookID= %s"
            values = (borrower_name, book_id)
            result2 = execute_query(query, values)

            if result2:
                st.error("This book is already borrowed by you.")
            else:

                # query = "INSERT INTO Borrowers (Name,BookID,Type) VALUES (%s,%s,'Borrow')"
                query = "INSERT INTO Borrowers (Name, BookID, Type, NoOfBooks) VALUES (%s, %s, 'Borrow', 1) ON DUPLICATE KEY UPDATE NoOfBooks = NoOfBooks + 1"
                values = (borrower_name, book_id)
                # borrower_id = execute_query(query, values)
                execute_query2(query, values)
                query = "SELECT BorrowerID FROM Borrowers WHERE Name = %s AND BookID = %s"
                borrower_id = execute_query(query, values)[0]['BorrowerID']

                query = "INSERT INTO Transactions (BookID, BorrowerID, TransactionDate, Type) VALUES (%s, %s, NOW(), 'Borrow')"
                values = (book_id, borrower_id)
                execute_query2(query, values)

                query = "UPDATE Books SET Quantity = Quantity - 1 WHERE BookID = %s"
                values = (book_id,)
                execute_query2(query, values)

                st.success("Book borrowed successfully!")

elif selected_option == "Return Book":
    return_book()
elif selected_option == "Registered Users":
    registered_users()
elif selected_option == "User Registration":
    user_registration()

connection.close()
