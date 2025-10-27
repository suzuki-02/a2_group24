from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import or_

from . import db
from .models import Event

main_bp = Blueprint("main", __name__)

_DEFAULT_FILTER = "all"


# -------------------------------
# Utility: Weekend date range
# -------------------------------
def _weekend_bounds(today: date) -> tuple[date, date]:
    """Return the Saturday/Sunday pair for the weekend covering `today`."""
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
    """Fetch events for the requested filter; defaults to upcoming."""
    today = datetime.today().date()
    query = Event.query.filter(Event.date != None)  # noqa: E711

    if filter_type == "today":
        query = query.filter(db.func.date(Event.date) == today)
    elif filter_type == "weekend":
        saturday, sunday = _weekend_bounds(today)
        query = query.filter(db.func.date(Event.date).between(saturday, sunday))
    elif filter_type == "past":
        query = query.filter(
            db.func.julianday(Event.date) < db.func.julianday(db.func.date("now"))
        )
    else:
        # treat "all" and unknown values as upcoming events
        query = query.filter(
            db.func.julianday(Event.date) >= db.func.julianday(db.func.date("now"))
        )

    return query.order_by(db.func.julianday(Event.date).asc()).all()


# -----------------------------------------
# Featured events (carousel population)
# -----------------------------------------
def _fetch_featured_events() -> list[Event]:
    """Return the featured events to show in the carousel (next 5 upcoming)."""
    return (
        Event.query.filter_by(featuredevent=True)
        .filter(Event.date != None)  # noqa: E711
        .filter(
            db.func.julianday(Event.date) >= db.func.julianday(db.func.date("now"))
        )
        .order_by(db.func.julianday(Event.date).asc())
        .limit(5)
        .all()
    )


# --------------------------------
# Safe query wrapper
# --------------------------------
def _safe_query(callable_, fallback=None):
    """Execute a query helper, logging failures and returning a fallback list."""
    try:
        return callable_()
    except Exception as ex:
        try:
            db.session.rollback()
        except Exception:
            pass
        try:
            from flask import current_app
            current_app.logger.exception("Query failed: %r", ex)
        except Exception:
            pass
        return [] if fallback is None else fallback()


# -----------------------------
# Home Page
# -----------------------------
@main_bp.route("/")
def index():
    """Main homepage with event list and featured carousel."""
    filter_type = request.args.get("filter", _DEFAULT_FILTER)

    # Fetch events for the selected filter
    events = _safe_query(lambda: _fetch_events(filter_type))
    if not events and filter_type != "weekend":
        # fallback to weekend events so homepage never feels empty
        events = _safe_query(lambda: _fetch_events("weekend"))

    # Fetch featured events for carousel
    featured_events = _safe_query(_fetch_featured_events)

    print(f"DEBUG: {len(events)} events found for filter '{filter_type}'")
    print(f"DEBUG: {len(featured_events)} featured events found")

    return render_template(
        "index.html",
        events=events,
        featured_events=featured_events,
        active_filter=filter_type,
    )


# -----------------------------
# AJAX Event Filtering
# -----------------------------
@main_bp.route("/events/filter")
def filter_events():
    """AJAX endpoint for filtering events by genre and/or date (today, weekend, etc.)."""
    filter_type = request.args.get("filter", _DEFAULT_FILTER)
    genre = request.args.get("genre", None)

    print(f"DEBUG: /events/filter called with filter='{filter_type}', genre='{genre}'")

    today = datetime.today().date()
    query = Event.query.filter(Event.date != None)

    # Genre filtering (case-insensitive)
    if genre and genre.lower() != "all":
        query = query.filter(db.func.lower(Event.genre) == genre.lower())

    # Date filtering
    if filter_type == "today":
        query = query.filter(db.func.date(Event.date) == today)
    elif filter_type == "weekend":
        saturday, sunday = _weekend_bounds(today)
        query = query.filter(db.func.date(Event.date).between(saturday, sunday))
    elif filter_type == "past":
        query = query.filter(
            db.func.julianday(Event.date) < db.func.julianday(db.func.date("now"))
        )
    else:
        query = query.filter(
            db.func.julianday(Event.date) >= db.func.julianday(db.func.date("now"))
        )

    events = query.order_by(db.func.julianday(Event.date).asc()).all()

    print(f"DEBUG: {len(events)} events found for genre='{genre}', filter='{filter_type}'")
    return render_template("_event_cards.html", events=events)

# Search Route

@main_bp.route("/search")
def search():
    query_text = request.args.get("search", "").strip()
    if not query_text:
        return redirect(url_for("main.index"))

    like_pattern = f"%{query_text}%"
    events = _safe_query(
        lambda: db.session.scalars(
            db.select(Event).where(
                or_(
                    Event.title.ilike(like_pattern),
                    Event.description.ilike(like_pattern),
                )
            )
        ).all()
    )

    featured_events = _safe_query(_fetch_featured_events)

    return render_template(
        "index.html",
        events=events,
        featured_events=featured_events,
        active_filter="search",
        search_query=query_text,
    )


# -----------------------------
# Error Handling
# -----------------------------
@main_bp.app_errorhandler(403)
def forbidden(e):
    """Custom 403 Forbidden error page."""
    return render_template("errors/403.html"), 403
