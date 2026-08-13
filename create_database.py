import sqlite3

connection = sqlite3.connect("favourites.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS favourites (
        id INTEGER PRIMARY KEY,
        link TEXT NOT NULL,
        saved_at TEXT,
        available INTEGER,
        checked_at TEXT
    )
""")

connection.commit()
connection.close()

print("Database Ready.")