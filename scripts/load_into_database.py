from favourites.database import connect, insert_favourites
from favourites.parse import FAVOURITES_FILE, load_favourites

favourites = load_favourites(FAVOURITES_FILE)

rows = [
    (favourite["Link"], favourite.get("Date"))
    for favourite in favourites
    if favourite["Link"] != ""
]

connection, cursor = connect()
inserted = insert_favourites(cursor, rows)
connection.commit()
connection.close()

print(f"Inserted {inserted} favourites.")
