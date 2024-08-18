import sqlite3

# Define the path to your database
DATABASE_PATH = 'db.db'

def list_tables_and_columns():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Retrieve the list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("Tables:")
    for table in tables:
        table_name = table[0]
        print(f" - {table_name}")
        
        # Retrieve columns for each table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print(f"  Columns in {table_name}:")
        for column in columns:
            column_name = column[1]  # The second item in the tuple is the column name
            column_type = column[2]  # The third item is the column type
            print(f"    - {column_name} ({column_type})")

    # Close the connection
    conn.close()

# Run the function to list tables and columns
list_tables_and_columns()
