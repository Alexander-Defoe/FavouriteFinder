# FavouriteFinder

A local tool for browsing the 16,000 TikTok videos I'd saved and could no
longer reach.

## The problem

TikTok's favourites are a lazy-loading feed. There's no search, no jump-to, no
filtering — the only way to reach something saved two years ago is to scroll
for twenty minutes and hope. Anything past the first few hundred items is
effectively lost.

There's also no way to tell which saved videos still exist. Creators delete
things and accounts go private, so a large share of any old collection is dead
links you only find by tapping them.

## What it does

**A web interface** — a grid of thumbnails that scrolls endlessly, and clicking
one plays the video full size over a dimmed page, with arrow keys to move
between videos.

**A command line** — instant access to any point in the collection (page 451
lands on item 9,001), search across creator names and captions, filtering by
date range and by whether the video still exists.

**Availability checking** against TikTok's official oEmbed endpoint, which also
recovers the creator, caption and thumbnail for every video — none of which are
in the export.

## What it found

**4,829 of my 16,134 saved videos — 30% — no longer exist.** The rate climbs
steeply with age: a sample of 2020 saves was about half dead. The collection
spans June 2020 to August 2026 across 8,301 different creators.

## How it works

```
TikTok data export (JSON)
  → favourites/parse.py              find the favourites section
  → scripts/create_database.py       define the SQLite schema
  → scripts/load_into_database.py    16,134 rows
  → scripts/check_availability.py    ask oEmbed about each video
  → scripts/fetch_thumbnails.py      download and shrink each thumbnail
  → browse.py                        command-line access
  → app.py                           web interface
```

```
favourites/   the library — imported, never run directly
scripts/      the jobs — run once, or when a new export arrives
templates/    web pages
static/       cached thumbnails
tests/
app.py        web interface
browse.py     command line
```

The export is treated as read-only; everything derived lives in SQLite.

**`favourites/database.py` is the data layer.** It owns the connection, the schema and
every SQL statement in the project. Nothing else imports `sqlite3`. Callers
pass intent — a search term, a date range, an availability flag — and never see
SQL, which is what made a second interface possible: `app.py` and `browse.py`
call the same two functions and differ only in how they collect input and
present output.

Both the row query and the count query build their `WHERE` from one shared
function, so a page count can't disagree with the rows on the page.

### Two things the data forced

**The availability job runs for hours, so it's built to be interrupted.**
`available` has three states — unchecked, available, gone. A failed request
leaves a row unchecked rather than marking it deleted, so a dropped connection
can't corrupt the results, and a restart picks up exactly where it stopped. A
plain yes/no column would have made "checked and gone" indistinguishable from
"not reached yet", and any interruption would mean starting over.

**Thumbnails are cached locally because TikTok's image URLs expire.** The
addresses oEmbed returns are signed with a two-day expiry — storing one is
storing a temporary access token, not an address. By the time the collection
was complete, 11,072 of 11,305 had already stopped working. `scripts/fetch_thumbnails.py`
fetches a fresh URL per video, downloads the image, shrinks it to card width and
saves it. Roughly 380 MB, and it skips anything already on disk so it can be
stopped and restarted.

## Usage

Web interface:

```bash
flask --app app run
```

Command line:

```bash
python browse.py                    # first page, newest first
python browse.py 451                # jump straight to item 9,001
python browse.py 1 --search pasta --available
python browse.py 1 --since 2025-01-01 --until 2025-12-31
python browse.py --help
```

```
$ python browse.py 1 --search pasta --available
Page 1 of 1 — showing 1-18 of 18
  2025-04-09 00:06:19  https://www.tiktokv.com/share/video/7490516612290809110/
      Eating with Tod · LONDON'S BIGGEST £85 ITALIAN BUFFET 🇮🇹 If you can't take a…
  2025-03-23 12:00:35  https://www.tiktokv.com/share/video/7470577740471733559/
      Blake Menard · Steak & Pasta 🥩🍝🧄 Recipe in bio #steak #pasta #food
```

## Getting started

### 1. Request your data from TikTok

In the TikTok app: **Profile → ☰ menu → Settings and privacy → Account →
Download your data**.

On the **Request data** tab choose **All data**, and set the file format to
**JSON** — the TXT option is human-readable but far more work to parse. Tap
**Request data**.

It usually arrives within a few hours, though TikTok allows up to a few days.
When it's ready, return to the same screen, open the **Download data** tab and
save the `.zip`. **The download link expires after about four days**, so don't
leave it.

### 2. Put the export where the code expects it

Unzip it, find the JSON file, and place it at:

```
data/user_data_tiktok.json
```

Create the `data/` folder if it isn't there. The filename matters — it's set
as `FAVOURITES_FILE` in `favourites/parse.py`. Rename your export to match, or
change that one line.

`data/` is gitignored. The export contains your direct messages, login history
and payment details alongside the favourites, so it must never reach a
repository.

### 3. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The virtual environment keeps this project's packages separate from everything
else on your machine. You'll need to run `source .venv/bin/activate` in each
new terminal.

### 4. Build the database

```bash
python -m scripts.create_database       # creates the table
python -m scripts.load_into_database    # reads the export in, ~10 seconds
```

Safe to run both again at any point. Re-importing a newer export adds only the
favourites that aren't already stored.

At this point the tool works — you can browse and search straight away. The two
jobs below add information the export doesn't contain.

### 5. Check which videos still exist

```bash
python -m scripts.check_availability
```

**About 3 hours.** The export tells you what you saved and when, and nothing
else. This asks TikTok's oEmbed endpoint about each video in turn, which
establishes whether it still exists and collects the creator, caption and
thumbnail — so it's also what makes searching by caption possible.

Requests are spaced half a second apart to stay polite. Leave it running and
come back.

### 6. Download the thumbnails

```bash
python -m scripts.fetch_thumbnails
```

**About 3 hours and 380 MB.** Needed because the image addresses collected in
step 5 expire after roughly two days. This fetches a fresh one per video and
saves the picture itself, so the grid keeps working indefinitely.

Skip this if you don't want the disk usage — everything else works, the grid
just shows empty cards.

### 7. Run it

```bash
flask --app app run
```

Then open **http://127.0.0.1:5000**.

---

**Both long jobs can be stopped and restarted freely.** Neither loses progress:
the availability check skips anything already checked, and the thumbnail
download skips anything already on disk. Interrupt them, close the laptop,
carry on tomorrow.

**You don't have to wait for either to finish.** Start the web interface and
refresh as they run — results appear as they're collected.

## Tests

```bash
pytest
```

40 tests: unit tests for the pagination, truncation, date-validation and
URL-parsing logic; a property test checking that every SQL placeholder has a
matching parameter across four argument combinations; and integration tests
running real queries against a temporary database built from the same schema as
production.

`scripts/make_mock_export.py` generates a synthetic export with the same structure as
the real one — including missing keys, blank links and duplicates — for working
against before an export arrives.

## Notes

Data comes only from TikTok's official export and their public oEmbed endpoint.
Nothing is scraped.

Videos play through TikTok's official embed, which means they start muted — the
player runs in a cross-origin iframe and can't be controlled from the page
around it.

The export and the database are gitignored, as are the cached thumbnails. The
export contains direct messages, login history and payment details alongside
the favourites.
