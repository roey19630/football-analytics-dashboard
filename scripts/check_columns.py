import sqlite3

# Path to SQLite database
db_sqlite_file = "../data/db_file.sqlite"

def check_columns():
    # Connect to SQLite database
    conn = sqlite3.connect(db_sqlite_file)
    cursor = conn.cursor()

    # Get the column names for the table 'fifa_players'
    cursor.execute("PRAGMA table_info(fifa_players);")
    columns = cursor.fetchall()

    print("Columns in 'fifa_players' table:")
    for column in columns:
        print(f"- {column[1]}")  # column[1] is the column name

    # Check if there are records in the table
    cursor.execute("SELECT COUNT(*) FROM fifa_players;")
    count = cursor.fetchone()[0]

    print(f"\nTotal rows in 'fifa_players': {count}")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    check_columns()
