import duckdb
import pandas as pd

# File paths
reduced_file = "../data/reduced_data.csv"
db_file = "../data/db_file.duckdb"

def load_data_to_duckdb():
    # Create a connection to the DuckDB database
    conn = duckdb.connect(db_file)
    print(f"Database created: {db_file}")

    # Load the reduced dataset into a Pandas DataFrame
    df = pd.read_csv(reduced_file)
    print(f"Reduced dataset loaded: {reduced_file} with {len(df)} rows.")

    # Create a table in DuckDB and load the data
    conn.execute("CREATE TABLE IF NOT EXISTS reduced_table AS SELECT * FROM df")
    print("Data loaded into the table 'reduced_table'.")

    # Confirm the created tables
    tables = conn.execute("SHOW TABLES").fetchall()
    print("Tables available in the database:")
    for table in tables:
        print(table[0])

    # Close the connection
    conn.close()
    print("DuckDB connection closed.")

if __name__ == "__main__":
    load_data_to_duckdb()
