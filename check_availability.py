import requests
import sqlite3
import time
from datetime import datetime

connection = sqlite3.connect("favourites.db")
cursor = connection.cursor()

query = "SELECT id, link FROM favourites WHERE available IS NULL"

rows = cursor.execute(query).fetchall()

checked = 0
consecutive_unknown = 0

for row in rows:
    video_row_id, link = row
    video_id = link.rstrip("/").split("/")[-1]
    video_url = f"https://www.tiktok.com/@x/video/{video_id}"

    try:
        response = requests.get(
            "https://www.tiktok.com/oembed",
            params={"url": video_url},
            timeout=15,
        )
    except requests.RequestException:
        continue

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if response.status_code == 200:
        data = response.json()
        available = 1
        title = data["title"]
        author = data["author_name"]
        thumbnail = data["thumbnail_url"]
    elif response.status_code == 400:
        available = 0
        title = None
        author = None
        thumbnail = None
    else:
        available = None
        consecutive_unknown += 1
        if consecutive_unknown >= 10:
            print(f"Stopping: {consecutive_unknown} unknown responses in a row (last was {response.status_code})")
            break


    if available is not None:
        cursor.execute(
            """
            UPDATE favourites
            SET available = ?, checked_at = ?, title = ?, author = ?, thumbnail = ?
            WHERE id = ?
            """,
            (available, now, title, author, thumbnail, video_row_id),
        )

    checked += 1

    if checked % 100 == 0:
        print(f"{checked} of {len(rows)} checked")
        connection.commit()

    time.sleep(0.5)

connection.commit()

connection.close()
