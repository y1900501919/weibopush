import sqlite3
sqlite_file = 'data.db'
conn = sqlite3.connect(sqlite_file)

def update_db():
    conn.commit()