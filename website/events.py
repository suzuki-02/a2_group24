from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Comment, Order
from flask_login import current_user, login_required
from .forms import EventForm, CommentForm, PurchaseForm, EventUpdateForm
from . import db
import os
from werkzeug.utils import secure_filename

events_bp = Blueprint('event', __name__, url_prefix='/events')


@events_bp.route('/<id>')
def show(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    cform = CommentForm()
    oform = PurchaseForm()
    return render_template('events/show.html', event=event, cform=cform, oform=oform)


@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    print('Method type:', request.method)
    form = EventForm()

    if request.method == 'POST':
        print("📩 Form submitted")
        print("Door time:", form.door_time.data, "| Start time:", form.start_time.data)

        # Check that start time is after door time
        
        if form.start_time.data and form.door_time.data:
            if form.start_time.data <= form.door_time.data:
                flash("Start time must be after door time.", "danger")
                print("❌ Flash triggered — start time is before or equal to door time.")
                return render_template('events/create.html', form=form)

    if form.validate_on_submit():
        db_file_path = check_upload_file(form)

        event = Event(
            title=form.title.data,
            venue=form.venue.data,
            genre=form.genre.data,
            date=form.date.data,
            start_time=form.start_time.data,
            door_time=form.door_time.data,
            price=form.price.data,
            quantity=form.quantity.data,
            description=form.description.data,
            image=db_file_path or '/static/image/default_event.jpg',
            featuredevent=form.featuredevent.data,
            creator=current_user
        )

        db.session.add(event)
        db.session.commit()
        print(f"✅ Event added with ID {event.id}")
        flash("Event created successfully!", "success")
        return redirect(url_for('event.show', id=event.id))
    else:
        if request.method == 'POST':
            print('❌ Validation failed:', form.errors)

    return render_template('events/create.html', form=form)


def check_upload_file(form):
    """Safely handle optional file uploads and return the image path or None."""
    fp = form.image.data

    if not fp:
        return None

    filename = secure_filename(fp.filename)
    if not filename:
        return None

    BASE_PATH = os.path.dirname(__file__)
    upload_path = os.path.join(BASE_PATH, 'static', 'image', filename)
    db_upload_path = '/static/image/' + filename

    fp.save(upload_path)
    return db_upload_path


@events_bp.route('/<id>/comment', methods=['POST'])
@login_required
def comment(id):
    form = CommentForm()
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if form.validate_on_submit():
        comment = Comment(text=form.text.data, event=event, user=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added', 'success')
    return redirect(url_for('event.show', id=id))


@events_bp.route('/<id>/purchase', methods=['POST'])
@login_required
def purchase(id):
    form = PurchaseForm()
    event = db.session.scalar(db.select(Event).where(Event.id == id))

    if form.validate_on_submit():
        quantity_requested = int(request.form.get('quantity', 1))

        if event.status != "Open":
            flash(f"Event is not open for booking. Current status: {event.status}", "warning")
            return redirect(url_for('event.show', id=id))
        if event.quantity <= 0:
            flash("Sorry, ticket is sold out for this event.", "danger")
            return redirect(url_for('event.show', id=id))
        if quantity_requested > event.quantity:
            flash(f"Only {event.quantity} tickets left.", "warning")
            return redirect(url_for('event.show', id=id))

        order = Order(
            user=current_user,
            event=event,
            quantity=quantity_requested,
            order_date=db.func.now()
        )
        order.calculate_total()

        event.quantity -= quantity_requested
        event.update_status()

        db.session.add(order)
        db.session.commit()

        flash(f"Booking confirmed! Order ID #{order.id}. Total: ${order.total_price:.2f}", "success")
    return redirect(url_for('event.show', id=id))


@events_bp.route('/books', methods=['GET'])
@login_required
def my_bookings():
    orders = current_user.orders
    return render_template('events/books.html', orders=orders)


@events_bp.route('/my_events')
@login_required
def my_events():
    events = Event.query.filter_by(creator_id=current_user.id).order_by(Event.date.desc()).all()
    return render_template('events/my_events.html', events=events)


@events_bp.route('/<id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if not event:
        flash("Event not found", "danger")
        return redirect(url_for('main.index'))
    if event.creator != current_user:
        flash("You do not have permission to update this event", "danger")
        return redirect(url_for('event.show', id=event.id))
    if event.status == "Cancelled":
        flash("This event has been cancelled and cannot be updated.", "warning")
        return redirect(url_for('event.show', id=event.id))

    form = EventUpdateForm()
    if form.validate_on_submit():
        if form.image.data:
            event.image = check_upload_file(form)
        event.title = form.title.data
        event.date = form.date.data
        event.price = form.price.data
        event.quantity = form.quantity.data
        event.description = form.description.data
        db.session.commit()
        flash("Event updated successfully", "success")
        return redirect(url_for('event.show', id=event.id))
    elif request.method == 'GET':
        form.title.data = event.title
        form.date.data = event.date
        form.price.data = event.price
        form.quantity.data = event.quantity
        form.description.data = event.description

    return render_template('events/create.html', form=form, event=event)


@events_bp.route('/<id>/cancel')
@login_required
def cancel(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if not event:
        flash("Event not found", "danger")
        return redirect(url_for('event.my_events'))
    if event.creator != current_user:
        flash("You do not have permission to cancel this event", "danger")
        return redirect(url_for('event.show', id=event.id))

    event.cancel()
    db.session.commit()
    flash("Event has been cancelled successfully.", "warning")
    return redirect(url_for('event.my_events'))


@events_bp.route('/genre/<genre_name>')
def genre_page(genre_name):
    events = Event.query.filter(Event.genre.ilike(genre_name)).order_by(Event.date.asc()).all()
    featured_events = Event.query.filter_by(featuredevent=True).limit(5).all()
    return render_template(
        "events/genre.html",
        genre_name=genre_name,
        events=events,
        featured_events=featured_events
    )
