from flask import Flask, render_template, request

from database import connect, fetch_favourites, count_favourites
from tiktok import video_id
from pagination import last_page_number

app = Flask(__name__)

@app.route("/")
def index():
    connection, cursor = connect()

    page_size = 20
    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * page_size
    total = count_favourites(cursor, available_only=True)
    last_page = last_page_number(total, page_size)
    rows = fetch_favourites(cursor, available_only=True, limit=page_size, offset=offset)

    connection.close()
    return render_template("index.html", rows=rows, video_id=video_id, page=page, last_page=last_page, total=total)
