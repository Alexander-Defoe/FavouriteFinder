from flask import Flask, render_template, request

from database import connect, count_favourites, fetch_favourites
from pagination import last_page_number
from tiktok import video_id

app = Flask(__name__)

PAGE_SIZE = 20


def page_of_favourites(page):
    """Rows for one page, plus how many favourites there are in total."""
    connection, cursor = connect()
    total = count_favourites(cursor, available_only=True)
    rows = fetch_favourites(
        cursor,
        available_only=True,
        limit=PAGE_SIZE,
        offset=(page - 1) * PAGE_SIZE,
    )
    connection.close()
    return rows, total


@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    rows, total = page_of_favourites(page)
    return render_template(
        "index.html",
        rows=rows,
        video_id=video_id,
        page=page,
        last_page=last_page_number(total, PAGE_SIZE),
        total=total,
    )


@app.route("/cards")
def cards():
    """Just the cards for one page, for the infinite scroll to append."""
    page = request.args.get("page", 1, type=int)
    rows, _ = page_of_favourites(page)
    return render_template("_cards.html", rows=rows, video_id=video_id)
