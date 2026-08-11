import sqlite3
from parse_favourites import load_favourites

favourites = load_favourites("data/user_data_tiktok.json")

connection = sqlite3.connect("favourites.db")
cursor = connection.cursor()

inserted = 0

for favourite in favourites:
    link = favourite["Link"]
    if link == "":
        continue
    cursor.execute(
        "INSERT INTO favourites (link, saved_at) VALUES (?, ?)",
        (link, favourite.get("Date")),
    )
    inserted += 1

connection.commit()
connection.close()

print(f"Inserted {inserted} favourites.")
