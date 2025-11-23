import sqlite3
import duckdb

# Paths to database files
duckdb_file = "../data/db_file.duckdb"
sqlite_file = "../data/db_file.sqlite"

# Connect to DuckDB
duckdb_conn = duckdb.connect(duckdb_file)

# Get column names from DuckDB
columns_info = duckdb_conn.execute("DESCRIBE fifa_players").fetchall()
columns = [col[0] for col in columns_info]  # Extract column names

# Connect to SQLite
sqlite_conn = sqlite3.connect(sqlite_file)
sqlite_cursor = sqlite_conn.cursor()

# Drop table if it exists
sqlite_cursor.execute("DROP TABLE IF EXISTS fifa_players;")

# Create table in SQLite dynamically
create_table_query = f"CREATE TABLE fifa_players ({', '.join(columns)});"
sqlite_cursor.execute(create_table_query)
sqlite_conn.commit()
print("✅ SQLite table structure created.")

# Get the total number of rows
total_rows = duckdb_conn.execute("SELECT COUNT(*) FROM fifa_players").fetchone()[0]
chunk_size = 50000  # Adjust chunk size based on memory capacity

print(f"Total rows to transfer: {total_rows}")
print(f"Processing in chunks of {chunk_size} rows...")

# Transfer data in chunks
offset = 0
while offset < total_rows:
    print(f"Processing rows {offset} to {offset + chunk_size}...")

    # Fetch chunk from DuckDB
    chunk = duckdb_conn.execute(f"SELECT * FROM fifa_players LIMIT {chunk_size} OFFSET {offset}").fetchdf()

    # Insert chunk into SQLite
    chunk.to_sql("fifa_players", sqlite_conn, if_exists="append", index=False)

    offset += chunk_size

print("Data successfully transferred in chunks!")

# Close connections
sqlite_conn.commit()
sqlite_conn.close()
duckdb_conn.close()
