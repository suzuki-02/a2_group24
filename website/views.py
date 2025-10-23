
from sqlalchemy import or_
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from .forms import CommentForm
from .models import Event, Comment

from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import select
from .models import Event
from . import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # filter: 'upcoming' (default), 'past', or 'all'
    filter_type = request.args.get('filter', 'upcoming')

    # Harden against query errors so the page still renders
    events = []
    try:
        stmt = select(Event)
        if filter_type == 'upcoming':
            stmt = stmt.where(Event.is_upcoming == True)   # noqa: E712
        elif filter_type == 'past':
            stmt = stmt.where(Event.is_upcoming == False)  # noqa: E712

        events = db.session.execute(stmt).scalars().all()
    except Exception as ex:
        # Log and continue rendering the page instead of 500
        try:
            # use app logger if available via current_app (optional)
            from flask import current_app
            current_app.logger.exception("Index query failed: %r", ex)
        except Exception:
            pass

    return render_template('index.html', events=events, active_filter=filter_type)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        stmt = select(Event).where(Event.user_id == current_user.id)
        user_events = db.session.execute(stmt).scalars().all()
    except Exception as ex:
        try:
            from flask import current_app
            current_app.logger.exception("Dashboard query failed: %r", ex)
        except Exception:
            pass
        user_events = []
    return render_template('dashboard.html', events=user_events)

@main_bp.route('/delete/<int:event_id>')
@login_required
def delete_event(event_id):
    # If your Flask-SQLAlchemy supports get_or_404:
    try:
        event = db.get_or_404(Event, event_id)
    except AttributeError:
        # Fallback for older FSQ versions
        event = db.session.get(Event, event_id)
        if not event:
            flash("Event not found.", "warning")
            return redirect(url_for('main.dashboard'))

    if event.user_id != current_user.id:
        flash("You cannot delete another user's event.", "danger")
        return redirect(url_for('main.dashboard'))
    else:
        events = (
            Event.query
            .filter(Event.date != None)
            .filter(db.func.julianday(Event.date) >= db.func.julianday(db.func.date('now')))
            .order_by(db.func.julianday(Event.date).asc())
            .all()
        )

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

@main_bp.app_errorhandler(403)
def forbidden(e):
    flash("You don't have permission to access that page.", "danger")
    return render_template('errors/403.html'), 403

