import json
from datetime import datetime

FAVOURITES_FILE = "data/user_data_tiktok.json"

def load_favourites(path):
    with open(path) as file:
        data = json.load(file)
    return data["Likes and Favorites"]["Favorite Videos"]["FavoriteVideoList"]

if __name__ == "__main__":
    favourites = load_favourites(FAVOURITES_FILE)

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