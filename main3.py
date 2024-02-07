import streamlit as st
import mysql.connector
from mysql.connector import Error

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

#new



#new
# Function to execute MySQL queries
def fetch_genres():
    query = "SELECT * FROM Genres"
    return execute_query(query)

def fetch_publishers():
    query = "SELECT * FROM Publishers"
    return execute_query(query)

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

# Function to add a new book to the database

#useless for now

def add_book(title, author, genre_id, publisher_id):
    # Establish a connection to the database
    connection = execute_query(query,values)

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

# Streamlit Interface

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

# Streamlit Interface
selected_option = st.sidebar.selectbox("Select Option", ["Home", "Add Book", "View Books", "Search Books", "Borrow Book"], key="select_option")

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
        genre = next((g for g in genres if g['GenreName'] == selected_genre), None) if selected_genre != "All Genres" else None
        publisher = next((p for p in publishers if p['PublisherName'] == selected_publisher), None) if selected_publisher != "All Publishers" else None

        # Perform search with filters
        search_results = search_books(title=title, author=author, genre=genre, publisher=publisher)

        # Display search results
        if search_results:
            st.subheader("Search Results:")
            for book in search_results:
                st.write(f"BookID: {book['BookID']}, Title: {book['Title']}, Author: {book['Author']}, Genre: {selected_genre}, Publisher: {selected_publisher}")
        else:
            st.warning("No books found matching the search criteria.")



if selected_option == "Home":
    st.write("Welcome to the Library Management System!")

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

    # Add a default option for better user experience
    # genre_names.insert(0, "Select Genre")
    # publisher_names.insert(0, "Select Publisher")

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
    query = "SELECT * FROM Books"
    books = execute_query(query)

    if books:
        for book in books:
            genre_id = book['GenreID']
            publisher_id = book['PublisherID']

            # Fetch genre name based on genre ID
            genre_name = next((g['GenreName'] for g in fetch_genres() if g['GenreID'] == genre_id), '')

            # Fetch publisher name based on publisher ID
            publisher_name = next((p['PublisherName'] for p in fetch_publishers() if p['PublisherID'] == publisher_id), '')

            st.write(
                f"BookID: {book['BookID']}, Title: {book['Title']}, Author: {book['Author']}, Quantity: {book['Quantity']}, Genre: {genre_name}, Publisher: {publisher_name}")
    else:
        st.warning("No books available in the library.")



elif selected_option == "Borrow Book":
    st.header("Borrow a Book")

    borrower_name = st.text_input("Borrower Name:")
    book_id = st.number_input("BookID:", min_value=1, step=1)

    if st.button("Borrow Book"):
        query = "INSERT INTO Borrowers (Name) VALUES (%s)"
        values = (borrower_name,)
        borrower_id = execute_query(query, values)

        query = "INSERT INTO Transactions (BookID, BorrowerID, TransactionDate, Type) VALUES (%s, %s, NOW(), 'Borrow')"
        values = (book_id, borrower_id)
        execute_query(query, values)

        query = "UPDATE Books SET Quantity = Quantity - 1 WHERE BookID = %s"
        values = (book_id,)
        execute_query(query, values)

        st.success("Book borrowed successfully!")

connection.close()