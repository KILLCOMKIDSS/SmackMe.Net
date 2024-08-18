import sqlite3

# Define the path to your SQLite database
DATABASE = 'db.db'

def recreate_users_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Drop the table if it exists
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # SQL command to create the users table with constraints
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT,
            phone TEXT,
            profile_pic TEXT,
            bio TEXT,
            is_admin INTEGER NOT NULL DEFAULT 0  -- Default value set to 0
        );
        '''
        cursor.execute(create_table_sql)
        conn.commit()
        print("Table 'users' recreated successfully.")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Close the database connection
        conn.close()

if __name__ == '__main__':
    recreate_users_table()
