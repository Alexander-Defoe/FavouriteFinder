import json
import random
from datetime import datetime, timedelta

random.seed(42)

entries = []

start_time = datetime(2021,4,22,4,5,3)

for number in range(300):
    random_id = random.randint(7000000000000000000, 7999999999999999999)

    offset = random.randint(0, 170_000_000)
    published = start_time + timedelta(seconds=offset)

    link = f"https://www.tiktokv.com/share/video/{random_id}/"

    if number > 0 and random.random() < 0.04:
        link = random.choice(entries)["Link"]

    if random.random() < 0.05:
        link = "" 

    entry = {
        "Date": published.strftime("%Y-%m-%d %H:%M:%S"),
        "Link": link,
    }
    if random.random() < 0.03:
        del entry["Date"]
    entries.append(entry)

export = {
    "Your Activity": {
        "Favorite Videos": {
            "FavoriteVideoList": entries,
        },
    },
}
with open("mock_data.json", "w") as file:
    json.dump(export, file, indent=2)