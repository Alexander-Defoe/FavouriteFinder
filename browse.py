import argparse
import sys
from database import connect, count_favourites, fetch_favourites

def last_page_number(total: int, page_size: int) -> int:
    return (total + page_size - 1) // page_size

def shorten(text: str | None, width: int) -> str:
    if not text:
        return ""
    if len(text) <= width:
        return text
    return text[:width] + "…"

if __name__ == "__main__":
    connection, cursor = connect()

    parser = argparse.ArgumentParser(description="Browse saved TikTok favourites")
    parser.add_argument("page", type=int, nargs="?", default=1)
    parser.add_argument("--search", default="")
    parser.add_argument("--available", action="store_true")
    parser.add_argument("--since", default="")
    parser.add_argument("--until", default="")

    args = parser.parse_args()

    page = args.page

    page_size = 20
    offset = (page - 1) * page_size

    total = count_favourites(cursor, args.search, args.available, args.since, args.until)

    last_page = last_page_number(total, page_size)

    if page < 1 or page > last_page:
        sys.exit(f"Page must be between 1 and {last_page}")

    end = min(offset + page_size, total)
    print(f"Page {page} of {last_page} — showing {offset + 1}-{end} of {total}")

    for row in fetch_favourites(cursor, args.search, args.available, page_size, offset,
                                since=args.since, until=args.until):
        print(f"  {row['saved_at']}  {row['link']}")
        print(f"      {shorten(row['author'], 20)} · {shorten(row['title'], 70)}")

    connection.close()
