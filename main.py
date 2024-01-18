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

# Streamlit Interface
selected_option = st.sidebar.selectbox("Select Option", ["Home", "Add Book", "View Books", "Borrow Book"])

if selected_option == "Home":
    st.write("Welcome to the Library Management System!")

elif selected_option == "Add Book":
    st.header("Add a New Book")

    title = st.text_input("Title:")
    author = st.text_input("Author:")
    quantity = st.number_input("Quantity:", min_value=0, step=1)

    # NEW CODE

    genres = fetch_genres()
    publishers = fetch_publishers()

    genre_names = [genre['GenreName'] for genre in genres]
    publisher_names = [publisher['PublisherName'] for publisher in publishers]

    # Add a default option for better user experience
    genre_names.insert(0, "Select Genre")
    publisher_names.insert(0, "Select Publisher")

    genre_selected = st.selectbox("Genre:", genre_names)
    publisher_selected = st.selectbox("Publisher:", publisher_names)

    # genre_selected = st.selectbox("Genre:", genres, format_func=lambda x: x['GenreName'] if x else '')
    # publisher_selected = st.selectbox("Publisher:", publishers, format_func=lambda x: x['PublisherName'] if x else '')

    #^^^^^^^^^^^^^^^^^^^
    if st.button("Add Book"):
        # query = "INSERT INTO Books (Title, Author, Quantity) VALUES (%s, %s, %s)"
        # values = (title, author, quantity)

        genre_id = genre_selected['GenreID'] if genre_selected else None
        publisher_id = publisher_selected['PublisherID'] if publisher_selected else None

        # Update the query to insert genre and publisher IDs
        query = "INSERT INTO Books (Title, Author, Quantity, GenreID, PublisherID) VALUES (%s, %s, %s, %s, %s)"
        values = (title, author, quantity, genre_id, publisher_id)


        execute_query(query, values)
        st.success("Book added successfully!")

elif selected_option == "View Books":
    st.header("View Books")
    query = "SELECT * FROM Books"
    books = execute_query(query)

    if books:
        for book in books:
            genre_name = fetch_genres()[0]['GenreName'] if fetch_genres() else ''
            publisher_name = fetch_publishers()[0]['PublisherName'] if fetch_publishers() else ''

            st.write(
                f"BookID: {book['BookID']}, Title: {book['Title']}, Author: {book['Author']}, Quantity: {book['Quantity']}, Genre: {genre_name}, Publisher: {publisher_name}")
    else:
        st.warning("No books available in the library.")
            # st.write(f"BookID: {book['BookID']}, Title: {book['Title']}, Author: {book['Author']}, Quantity: {book['Quantity']}")
    # else:
    #     st.warning("No books available in the library.")

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

# ... (previous code)

# ... (rest of the previous code)


# Close the database connection
connection.close()
