import argparse
import sqlite3
import sys

def last_page_number(total: int, page_size: int) -> int:
    return (total + page_size - 1) // page_size

connection = sqlite3.connect("favourites.db")
cursor = connection.cursor()

parser = argparse.ArgumentParser(description="Browse saved TikTok favourites")
parser.add_argument("page", type=int, nargs="?", default=1)
parser.add_argument("--search", default="")
parser.add_argument("--available", action="store_true")
args = parser.parse_args()

page = args.page
search = f"%{args.search}%"

conditions = ["COALESCE(author, '') LIKE ?"]
params = [search]

if args.available:
    conditions.append("available = 1")

where_clause = " AND ".join(conditions)

page_size = 20
offset = (page - 1) * page_size

count_query = f"""
    SELECT COUNT(*)
    FROM favourites
    WHERE {where_clause}
"""


total = cursor.execute(count_query, tuple(params)).fetchone()[0]

last_page = last_page_number(total, page_size)

if page < 1 or page > last_page:
    sys.exit(f"Page must be between 1 and {last_page}")

query = f"""
    SELECT saved_at, link, author
    FROM favourites
    WHERE {where_clause}
    ORDER BY saved_at DESC NULLS LAST
    LIMIT ?
    OFFSET ?
"""

end = min(offset + page_size, total)
print(f"Page {page} of {last_page} — showing {offset + 1}-{end} of {total}")

for row in cursor.execute(query, tuple(params + [page_size, offset])):
    print(f"  {row[0]}  {row[2]}  {row[1]}")

connection.close()
