# FavouriteFinder

A local tool for searching the 16,000 TikTok videos I'd saved and could no longer reach.

## The problem

TikTok's favourites section is difficult to navigate for older videos. There's no search, no jump-to,
no filtering — the only way to reach something saved two years ago is to
scroll for twenty minutes and hope. Anything past the first few hundred items
is effectively lost.

There's also no way to tell which saved videos still exist. Creators delete
things and accounts go private, so a large share of any old collection is
dead links you only discover by tapping them.

## What it does

- **Instant access to any point** in 16,134 favourites — page 451 lands on
  item 9,001 with no scrolling
- **Search** across creator names and video captions
- **Filter by date range**, and by whether the video still exists
- **Availability checking** against TikTok's official oEmbed endpoint, which
  also recovers the creator, caption and thumbnail — none of which are in the
  export

## What it found

**4,829 of my 16,134 saved videos — 30% — no longer exist.** The rate climbs
steeply with age: a sample of 2020 saves was about half dead. The collection
spans June 2020 to August 2026 across 8,301 different creators.

## How it works

```
TikTok data export (JSON)
  → parse_favourites.py     find the favourites section, report data quality
  → create_database.py      define the SQLite schema
  → load_into_database.py   16,134 rows
  → check_availability.py   ask oEmbed about each video, store the result
  → browse.py               paginated, searchable command-line access
```

The export is treated as read-only; everything derived lives in SQLite.

`database.py` is the data layer — it owns the connection, the schema and
every SQL statement. `browse.py` contains no SQL at all: it passes intent
(a search term, a date range, an availability flag) and prints what comes
back. Both the row query and the count query build their `WHERE` from one
shared function, so the page count can't disagree with the rows.

The availability job makes 16,134 HTTP requests over several hours, so it's
built to survive interruption. `available` has three states — unchecked,
available, gone — which means a failed request is distinguishable from a
deleted video, and a restart resumes exactly where it stopped rather than
starting over.

## Setup

Requires Python 3.13 and a TikTok data export in JSON format, requested from
Settings → Account → Download your data.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python create_database.py
python load_into_database.py
python check_availability.py        # several hours; resumable
python browse.py
```

## Tests

```bash
pytest
```

35 tests: unit tests for the pagination, truncation and date-validation
logic; a property test checking that every SQL placeholder has a matching
parameter across four argument combinations; and integration tests running
real queries against a temporary database built from the same schema as
production.
