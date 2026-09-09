from database import connect, insert_favourites
from parse_favourites import load_favourites

favourites = load_favourites("data/user_data_tiktok.json")

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
