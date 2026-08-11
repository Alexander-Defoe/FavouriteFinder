import sqlite3

connection = sqlite3.connect("favourites.db")
cursor = connection.cursor()

query = """
    SELECT saved_at, link
    FROM favourites
    ORDER BY saved_at ASC NULLS LAST
    LIMIT 10
"""

for row in cursor.execute(query):
    print(f"{row[0]}  {row[1]}")

connection.close()