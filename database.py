# Import sqlite3 so Python can work with SQLite databases.
import sqlite3


# This is the path/name of our SQLite database file.
DATABASE = "memory.db"


# ---------------------------------------------------------
# Create the database and messages table
# ---------------------------------------------------------
def init_db():
    # Connect to the SQLite database.
    # If memory.db doesn't exist, SQLite creates it automatically.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor.
    # The cursor is used to execute SQL commands.
    cursor = connection.cursor()

    # Create the messages table if it doesn't already exist.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    # Save the changes.
    connection.commit()

    # Close the database connection.
    connection.close()


# ---------------------------------------------------------
# Save a message
# ---------------------------------------------------------
def save_message(role, content):
    # Open the database.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor.
    cursor = connection.cursor()

    # Insert the message into the database.
    cursor.execute(
        "INSERT INTO messages (role, content) VALUES (?, ?)",
        (role, content)
    )

    # Save the change.
    connection.commit()

    # Close the connection.
    connection.close()


# ---------------------------------------------------------
# Load all previous messages
# ---------------------------------------------------------
def load_messages():
    # Open the database.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor.
    cursor = connection.cursor()

    # Get all messages in the order they were saved.
    cursor.execute(
        "SELECT role, content FROM messages ORDER BY id ASC"
    )

    # Fetch the results.
    messages = cursor.fetchall()

    # Close the connection.
    connection.close()

    # Convert the database rows into dictionaries.
    return [
        {
            "role": role,
            "content": content
        }
        for role, content in messages
    ]


# ---------------------------------------------------------
# Clear all messages
# ---------------------------------------------------------
def clear_messages():
    # Open the database.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor.
    cursor = connection.cursor()

    # Delete every saved message.
    cursor.execute("DELETE FROM messages")

    # Save the change.
    connection.commit()

    # Close the connection.
    connection.close()


# ---------------------------------------------------------
# Test database initialization
# ---------------------------------------------------------
if __name__ == "__main__":
    # Create the database/table.
    init_db()

    # Show a confirmation message.
    print("Database initialized successfully.")