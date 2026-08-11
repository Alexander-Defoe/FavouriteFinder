import json
from datetime import datetime

favourites_file = "mock_data.json"

def load_favourites(path):
    with open(path) as file:
        data = json.load(file)
    return data["Your Activity"]["Favorite Videos"]["FavoriteVideoList"]


favourites = load_favourites(favourites_file)

total = 0
missing_dates = 0
missing_link = 0
videos_2025 = 0

unique_links = set()

for favourite in favourites:
    total += 1

    if favourite["Link"] == "":
        missing_link += 1
    else: 
        unique_links.add(favourite["Link"])

    if favourite.get("Date") is None:
        missing_dates += 1
    else:
        date = favourite.get("Date")
        date_format = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        if date_format.year == 2025:
            videos_2025 += 1

duplicate_count = (total - missing_link) - len(unique_links)

print(f"There are {total} videos in total.")
print(f"There are {missing_dates} videos missing dates.")
print(f"There are {missing_link} videos missing a link.")
print(f"There are {duplicate_count} duplicate links.")
print(f"There are {videos_2025} videos from 2025.")