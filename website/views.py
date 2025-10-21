from sqlalchemy import or_
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from .forms import CommentForm
from .models import Event, Comment

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

# @main_bp.route('/search')
# def search():
#     # get inputs safely
#     q   = (request.args.get('q') or '').strip()
#     loc = (request.args.get('loc') or '').strip()

#     # if nothing was typed, just go back to home (avoids None returns)
#     if not q and not loc:
#         return redirect(url_for('main.index'))

#     # build query
#     query = Event.query
#     if q:
#         like = f"%{q}%"
#         query = query.filter(or_(Event.title.ilike(like),
#                                  Event.description.ilike(like)))
#     # only filter by location if your model has a 'location' column
#     if loc and hasattr(Event, 'location'):
#         query = query.filter(Event.location.ilike(f"%{loc}%"))

#     events = query.order_by(Event.date.asc()).all()

#     # ALWAYS return a template

#     # Get one event (e.g., the most recent)
#     event = db.session.scalar(db.select(Event).order_by(Event.id.desc()))
#     return render_template('index.html', event=event)
# in website/views.py (already done)
@main_bp.route('/search')
def search():
    q = (request.args.get('q') or '').strip()
    loc = (request.args.get('loc') or '').strip()

    stmt = db.select(Event)
    if q:
        stmt = stmt.where(Event.title.ilike(f'%{q}%') | Event.description.ilike(f'%{q}%'))
    if loc and hasattr(Event, 'location'):
        stmt = stmt.where(Event.location.ilike(f'%{loc}%'))

    events = db.session.scalars(stmt).all()

    return render_template('search_results.html', q=q, loc=loc, events=events)
