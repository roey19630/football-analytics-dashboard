import duckdb

# Paths
csv_file = "../data/reduced_data.csv"   #for reduced dataset
#csv_file = "../data/male_players_23.csv"        #for full dataset
duckdb_file = "../data/db_file.duckdb"

# Connect to DuckDB
conn = duckdb.connect(duckdb_file)

# Create table and load data from CSV
conn.execute("""
    CREATE TABLE IF NOT EXISTS fifa_players AS 
    SELECT * FROM read_csv_auto('{}');
""".format(csv_file))

# Verify the table was created
result = conn.execute("SHOW TABLES;").fetchall()
print("Tables in DuckDB:", result)

conn.close()
print(" Data successfully loaded into DuckDB.")
