from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from .models import Event
from . import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    filter_type = request.args.get("filter", "all")
    today = datetime.today().date()

    # --- TODAY ---
    if filter_type == "today":
        events = (
            Event.query
            .filter(db.func.date(Event.date) == today)
            .order_by(db.func.julianday(Event.date).asc())
            .all()
        )

    # --- THIS WEEKEND ---
    elif filter_type == "weekend":
        weekday = today.weekday()

        if weekday <= 4:
            saturday = today + timedelta(days=(5 - weekday))
        else:
            saturday = today if weekday == 5 else today - timedelta(days=1)

        sunday = saturday + timedelta(days=1)

        events = (
            Event.query
            .filter(db.func.date(Event.date).between(saturday, sunday))
            .order_by(db.func.julianday(Event.date).asc())
            .all()
        )

    # --- ALL UPCOMING EVENTS (default) ---
    else:
        events = (
            Event.query
            .filter(Event.date != None)
            .filter(db.func.julianday(Event.date) >= db.func.julianday(db.func.date('now')))
            .order_by(db.func.julianday(Event.date).asc())
            .all()
        )

    print(f"DEBUG: {len(events)} events found for filter '{filter_type}'")
    return render_template('index.html', events=events, active_filter=filter_type)

@main_bp.route('/events/filter')
def filter_events():
    filter_type = request.args.get("filter", "all")
    today = datetime.today().date()

    if filter_type == "today":
        events = (
            Event.query
            .filter(db.func.date(Event.date) == today)
            .order_by(db.func.julianday(Event.date).asc())
            .all()
        )

    elif filter_type == "weekend":
        weekday = today.weekday()
        if weekday <= 4:
            saturday = today + timedelta(days=(5 - weekday))
        else:
            saturday = today if weekday == 5 else today - timedelta(days=1)
        sunday = saturday + timedelta(days=1)

        events = (
            Event.query
            .filter(db.func.date(Event.date).between(saturday, sunday))
            .order_by(db.func.julianday(Event.date).asc())
            .all()
        )

    else:
        events = (
            Event.query
            .filter(Event.date != None)
            .filter(db.func.julianday(Event.date) >= db.func.julianday(db.func.date('now')))
            .order_by(db.func.julianday(Event.date).asc())
            .all()
        )

    # 👇 Only render the event cards section, not the full page
    return render_template('_event_cards.html', events=events)

