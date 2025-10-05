from flask import Blueprint, render_template
from .models import Event
from . import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # Get one event (e.g., the most recent)
    event = db.session.scalar(db.select(Event).order_by(Event.id.desc()))
    return render_template('index.html', event=event)
