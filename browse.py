import sqlite3
import sys

connection = sqlite3.connect("favourites.db")
cursor = connection.cursor()

if len(sys.argv) > 1:
    try:
        page = int(sys.argv[1])
    except ValueError:
        sys.exit("Page must be a whole number")
else:
    page = 1

if len(sys.argv) > 2:
    search = f"%{sys.argv[2]}%"
else:
    search = "%"

page_size = 20
offset = (page - 1) * page_size

count_query = ("""
    SELECT COUNT(*) 
    FROM favourites 
    WHERE COALESCE(author, '') 
    LIKE ?""")

total = cursor.execute(count_query, (search,)).fetchone()[0]

last_page = (total + page_size - 1) // page_size

if page < 1 or page > last_page:
    sys.exit(f"Page must be between 1 and {last_page}")

query = """
    SELECT saved_at, link, author
    FROM favourites
    WHERE COALESCE(author, '') LIKE ?
    ORDER BY saved_at DESC NULLS LAST
    LIMIT ?
    OFFSET ?
"""

end = min(offset + page_size, total)
print(f"Page {page} of {last_page} — showing {offset + 1}-{end} of {total}")

for row in cursor.execute(query, (search, page_size, offset)):
    print(f"  {row[0]}  {row[2]}  {row[1]}")

connection.close()
