import sys
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

from favourites.database import available_favourites, connect
from favourites.tiktok import video_id

THUMB_DIR = Path("static/thumbs")
OEMBED = "https://www.tiktok.com/oembed"
WIDTH = 400
PAUSE = 0.5

limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

THUMB_DIR.mkdir(parents=True, exist_ok=True)
connection, cursor = connect()
rows = available_favourites(cursor)
connection.close()

saved = skipped = failed = 0

for row in rows:
    identifier = video_id(row["link"])
    path = THUMB_DIR / f"{identifier}.jpg"

    if path.exists():
        skipped += 1
        continue

    try:
        meta = requests.get(
            OEMBED,
            params={"url": f"https://www.tiktok.com/@x/video/{identifier}"},
            timeout=15,
        )
        url = meta.json().get("thumbnail_url") if meta.status_code == 200 else None
        if not url:
            failed += 1
        else:
            picture = requests.get(url, timeout=20)
            image = Image.open(BytesIO(picture.content))
            image.thumbnail((WIDTH, WIDTH * 3))
            image.convert("RGB").save(path, "JPEG", quality=80)
            saved += 1
    except (requests.RequestException, OSError, ValueError):
        failed += 1

    if (saved + failed) % 50 == 0 and saved + failed:
        print(f"{saved} saved, {failed} failed, {skipped} already had")

    if limit and saved + failed >= limit:
        break

    time.sleep(PAUSE)

print(f"Done. {saved} saved, {failed} failed, {skipped} already had.")
