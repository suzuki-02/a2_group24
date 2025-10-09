from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from .forms import CommentForm
from .models import Event, Comment
from . import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # Get one event (e.g., the most recent)
    event = db.session.scalar(db.select(Event).order_by(Event.id.desc()))
    return render_template('index.html', event=event)
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
