import time
from datetime import datetime

import requests

from favourites.database import connect, record_availability, unchecked_favourites
from favourites.tiktok import video_id as extract_video_id

connection, cursor = connect()
rows = unchecked_favourites(cursor)

checked = 0
consecutive_unknown = 0

for row in rows:
    video_row_id, link = row
    video_id = extract_video_id(link)
    video_url = f"https://www.tiktok.com/@x/video/{video_id}"

    try:
        response = requests.get(
            "https://www.tiktok.com/oembed",
            params={"url": video_url},
            timeout=15,
        )
    except requests.RequestException:
        time.sleep(0.5)
        continue

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if response.status_code == 200:
        data = response.json()
        available = 1
        title = data["title"]
        author = data["author_name"]
        thumbnail = data["thumbnail_url"]
        consecutive_unknown = 0
    elif response.status_code == 400:
        available = 0
        title = None
        author = None
        thumbnail = None
        consecutive_unknown = 0
    else:
        available = None
        consecutive_unknown += 1
        if consecutive_unknown >= 10:
            print(f"Stopping: {consecutive_unknown} unknown responses in a row (last was {response.status_code})")
            break


    if available is not None:
        record_availability(cursor, video_row_id, available, now,
                            title=title, author=author, thumbnail=thumbnail)

    checked += 1

    if checked % 100 == 0:
        print(f"{checked} of {len(rows)} checked")
        connection.commit()

    time.sleep(0.5)

connection.commit()

connection.close()
