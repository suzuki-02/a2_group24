from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from .forms import EventForm, CommentForm
from .models import Event, Comment
from . import db

main_bp = Blueprint('main', __name__)

#uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'image')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def _save_image(file_storage):
    if not file_storage:
        return None
    filename = secure_filename(file_storage.filename)
    if not filename:
        return None
    fullpath = os.path.join(UPLOAD_FOLDER, filename)
    file_storage.save(fullpath)
    # return path relative to /static for url_for('static', filename=...)
    return f"image/{filename}"

@main_bp.route('/')
def index():
    # show the most recent event on the home page
    event = db.session.scalar(db.select(Event).order_by(Event.id.desc()))
    return render_template('index.html', event=event)

#  CREATE EVENT
@main_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create a new event (title, description, image)."""
    form = EventForm()
    if form.validate_on_submit():
        image_relpath = _save_image(form.image.data)

        ev = Event(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            image=image_relpath
        )
        db.session.add(ev)
        db.session.commit()
        flash('Event created!', 'success')
        # after create, go to that event's detail page
        return redirect(url_for('main.event_detail', event_id=ev.id))

    return render_template('events/create.html', form=form)

# SHOW EVENT + COMMENTS
@main_bp.route('/events/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    """Show one event; allow users to post a comment on it."""
    ev = db.session.get(Event, event_id)
    if not ev:
        abort(404)

    form = CommentForm()  
    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data.strip(),
            event=ev,
            user_id=getattr(current_user, 'id', None)  
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted!', 'success')
        return redirect(url_for('main.event_detail', event_id=event_id))

    
    return render_template('events/show.html', event=ev, form=form)
