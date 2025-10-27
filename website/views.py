from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import or_

from . import db
from .models import Event

main_bp = Blueprint("main", __name__)

# -------------------------------
# Utility: Weekend date range
# -------------------------------
def _weekend_bounds(today: date) -> tuple[date, date]:
    weekday = today.weekday()  # Monday=0, Sunday=6
    if weekday <= 4:
        saturday = today + timedelta(days=(5 - weekday))
    else:
        saturday = today if weekday == 5 else today - timedelta(days=1)
    sunday = saturday + timedelta(days=1)
    return saturday, sunday


# -------------------------------------
# Event query helpers (with filters)
# -------------------------------------
def _fetch_events(filter_type: str) -> list[Event]:
    today = datetime.today().date()
    query = Event.query.filter(Event.date != None)  # noqa: E711

    if filter_type == "today":
        query = query.filter(db.func.date(Event.date) == today)
    elif filter_type == "weekend":
        saturday, sunday = _weekend_bounds(today)
        query = query.filter(db.func.date(Event.date).between(saturday, sunday))
    elif filter_type == "past":
        query = query.filter(db.func.julianday(Event.date) < db.func.julianday(db.func.date("now")))
    else:
        query = query.filter(db.func.julianday(Event.date) >= db.func.julianday(db.func.date("now")))

    events = query.order_by(db.func.julianday(Event.date).asc()).all()

    # ✅ Fallback: show everything if no events match
    if not events:
        events = Event.query.order_by(db.func.julianday(Event.date).asc()).all()

    return events


# -----------------------------------------
# Featured events (carousel)
# -----------------------------------------
def _fetch_featured_events() -> list[Event]:
    return (
        Event.query.filter_by(featuredevent=True)
        .filter(Event.date != None)  # noqa: E711
        .order_by(db.func.julianday(Event.date).asc())
        .limit(5)
        .all()
    )


# -----------------------------
# Home Page
# -----------------------------
@main_bp.route("/")
def index():
    """Main homepage with event list and featured carousel."""
    filter_type = request.args.get("filter", "all")

    # Fetch events
    events = _fetch_events(filter_type)

    # Fetch featured events
    featured_events = _fetch_featured_events()

    print(f"[DEBUG] {len(events)} events found for '{filter_type}'")
    print(f"[DEBUG] {len(featured_events)} featured events found")

    return render_template(
        "index.html",
        events=events,
        featured_events=featured_events,
        active_filter=filter_type,
    )


# -----------------------------
# AJAX Date Filtering Only
# -----------------------------
@main_bp.route("/events/filter")
def filter_events():
    """AJAX endpoint for filtering events by date only."""
    filter_type = request.args.get("filter", "all")

    today = datetime.today().date()
    query = Event.query.filter(Event.date != None)

    # Date filtering
    if filter_type == "today":
        query = query.filter(db.func.date(Event.date) == today)
    elif filter_type == "weekend":
        saturday, sunday = _weekend_bounds(today)
        query = query.filter(db.func.date(Event.date).between(saturday, sunday))
    elif filter_type == "past":
        query = query.filter(db.func.julianday(Event.date) < db.func.julianday(db.func.date("now")))
    else:
        query = query.filter(db.func.julianday(Event.date) >= db.func.julianday(db.func.date("now")))

    events = query.order_by(db.func.julianday(Event.date).asc()).all()

    if not events:
        events = Event.query.order_by(db.func.julianday(Event.date).asc()).all()

    print(f"[DEBUG] {len(events)} events after filtering by date '{filter_type}'")
    return render_template("_event_cards.html", events=events)


# -----------------------------
# Genre Page (static link)
# -----------------------------
@main_bp.route("/genre/<genre_name>")
def genre_page(genre_name):
    """Display events for a specific genre (linked from genre buttons)."""
    events = (
        Event.query.filter(Event.genre.ilike(genre_name))
        .order_by(db.func.julianday(Event.date).asc())
        .all()
    )
    print(f"[DEBUG] {len(events)} events found for genre '{genre_name}'")

    return render_template("events/genre.html", genre_name=genre_name, events=events)


# -----------------------------
# Search Route
# -----------------------------
@main_bp.route("/search")
def search():
    query_text = request.args.get("search", "").strip()
    if not query_text:
        return redirect(url_for("main.index"))

    like_pattern = f"%{query_text}%"
    events = db.session.scalars(
        db.select(Event).where(
            or_(Event.title.ilike(like_pattern), Event.description.ilike(like_pattern))
        )
    ).all()

    featured_events = _fetch_featured_events()

    return render_template(
        "index.html",
        events=events,
        featured_events=featured_events,
        active_filter="search",
        search_query=query_text,
    )
