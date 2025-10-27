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
    saturday = today + timedelta(days=(5 - weekday)) if weekday <= 4 else today if weekday == 5 else today - timedelta(days=1)
    sunday = saturday + timedelta(days=1)
    return saturday, sunday


# -------------------------------------
# Event query helpers (with filters)
# -------------------------------------
def _fetch_events(filter_type: str) -> list[Event]:
    today = date.today()

    query = Event.query.filter(Event.date != None)  # noqa: E711

    if filter_type == "today":
        # Match events where the date equals today
        query = query.filter(Event.date == today)

    elif filter_type == "weekend":
        # Only show events this coming Saturday/Sunday
        saturday, sunday = _weekend_bounds(today)
        query = query.filter(Event.date >= saturday, Event.date <= sunday)

    elif filter_type == "past":
        # Only show events before today
        query = query.filter(Event.date < today)

    else:
        # Default: upcoming events (today or later)
        query = query.filter(Event.date >= today)

    events = query.order_by(Event.date.asc()).all()

    # ✅ Only fallback if *no events exist at all*
    if not events and filter_type == "all":
        events = Event.query.order_by(Event.date.asc()).all()

    return events


# -----------------------------------------
# Featured events (carousel)
# -----------------------------------------
def _fetch_featured_events() -> list[Event]:
    today = date.today()
    return (
        Event.query.filter_by(featuredevent=True)
        .filter(Event.date != None)  # noqa: E711
        .filter(Event.date >= today)
        .order_by(Event.date.asc())
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
    today = date.today()

    query = Event.query.filter(Event.date != None)

    if filter_type == "today":
        query = query.filter(Event.date == today)
    elif filter_type == "weekend":
        saturday, sunday = _weekend_bounds(today)
        query = query.filter(Event.date >= saturday, Event.date <= sunday)
    elif filter_type == "past":
        query = query.filter(Event.date < today)
    else:
        query = query.filter(Event.date >= today)

    events = query.order_by(Event.date.asc()).all()

    if not events and filter_type == "all":
        events = Event.query.order_by(Event.date.asc()).all()

    print(f"[DEBUG] {len(events)} events after filtering by date '{filter_type}'")
    return render_template("_event_cards.html", events=events)

# -----------------------------
# Search Route
# -----------------------------
@main_bp.route("/search")
def search():
    """Search events by title or description."""
    query_text = request.args.get("search", "").strip()
    if not query_text:
        return redirect(url_for("main.index"))

    like_pattern = f"%{query_text}%"
    events = db.session.scalars(
        db.select(Event).where(
            or_(
                Event.title.ilike(like_pattern),
                Event.description.ilike(like_pattern)
            )
        )
    ).all()

    featured_events = _fetch_featured_events()

    print(f"[DEBUG] Search returned {len(events)} results for query '{query_text}'")

    return render_template(
        "index.html",
        events=events,
        featured_events=featured_events,
        active_filter="search",
        search_query=query_text,
    )
