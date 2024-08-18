import sqlite3

def initialize_db():
    conn = sqlite3.connect('db.db')  # Adjust the path as needed
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

if __name__ == '__main__':
    initialize_db()
