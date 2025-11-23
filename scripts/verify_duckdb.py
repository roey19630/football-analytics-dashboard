import duckdb

# Path to the DuckDB database file
db_file = "../data/db_file.duckdb"

def verify_tables_in_duckdb():
    # Connect to the DuckDB database
    conn = duckdb.connect(db_file)
    print("Connected to DuckDB.")

    # Show all tables in the database
    tables = conn.execute("SHOW TABLES").fetchall()
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")

    # Check contents of each table (optional)
    for table in tables:
        print(f"\nPreview of table: {table[0]}")
        query = f"SELECT * FROM {table[0]} LIMIT 10"
        result = conn.execute(query).df()
        print(result)

    # Close the connection
    conn.close()
    print("DuckDB connection closed.")

if __name__ == "__main__":
    verify_tables_in_duckdb()
