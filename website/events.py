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
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    cform = CommentForm()
    oform = PurchaseForm()
    return render_template('events/show.html', event=event, cform=cform, oform=oform)

@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  print('Method type: ', request.method)
  form = EventForm()
  if form.validate_on_submit():
    db_file_path = check_upload_file(form)
    event = Event(
    title=form.title.data,
    date=form.date.data,
    price=form.price.data,
    quantity=form.quantity.data,
    description=form.description.data, 
    image = db_file_path,
    creator=current_user)
    db.session.add(event)
    db.session.commit()
    return redirect(url_for('event.show', id=event.id))
  return render_template('events/create.html', form=form)

def check_upload_file(form):
  # get file data from form  
  fp = form.image.data
  filename = fp.filename
  # get the current path of the module file… store image file relative to this path  
  BASE_PATH = os.path.dirname(__file__)
  # upload file location – directory of this file/static/image
  upload_path = os.path.join(BASE_PATH, 'static', 'image', secure_filename(filename))
  # store relative path in DB as image location in HTML is relative
  db_upload_path = '/static/image/' + secure_filename(filename)
  # save the file and return the db upload path  
  fp.save(upload_path)
  return db_upload_path

@events_bp.route('/<id>/comment', methods=['GET', 'POST'])
@login_required
def comment(id):  
    form = CommentForm()  
    # get the event object associated to the page and the comment
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    if form.validate_on_submit():  
      # read the comment from the form
      comment = Comment(text=form.text.data, event=event, user=current_user) 
      # here the back-referencing works - comment.event is set
      # and the link is created
      db.session.add(comment) 
      db.session.commit() 
 
      flash('Your comment has been added', 'success') 
    # using redirect sends a GET request to event.show
    return redirect(url_for('event.show', id=id))

@events_bp.route('/<id>/purchase', methods=['POST'])
@login_required
def purchase(id):
    form = PurchaseForm()

    event = db.session.scalar(db.select(Event).where(Event.id==id))
    if form.validate_on_submit():  

      quantity_requested = int(request.form.get('quantity', 1))

      # Validate ticket availability
      if event.status != "Open":
        flash(f"Event is not open for booking. Current status: {event.status}", "warning")
      if event.quantity <= 0:
        flash("Sorry, ticket is sold out for this event.", "danger")
        return redirect(url_for('event.show', id=id))
      if quantity_requested > event.quantity:
        flash(f"Only {event.quantity} tickets left.", "warning")
        return redirect(url_for('event.show', id=id))

      # Create order and compute price
      order = Order(
          user=current_user,
          event=event,
          quantity=quantity_requested,
          order_date=db.func.now()
      )
      order.calculate_total()

      # Update event quantity
      event.quantity -= quantity_requested

      # Update event status if needed (this should called only after quantity change)
      event.update_status()

      db.session.add(order)
      db.session.commit()

      flash(f"Booking confirmed! Order ID #{order.id}. Total: ${order.total_price:.2f}", "success")
    return redirect(url_for('event.show', id=id))

@events_bp.route('/books', methods=['GET'])
@login_required
def my_bookings():
    # get all orders by current user
    orders = current_user.orders  # because of the backref
    return render_template('events/books.html', orders=orders)

@events_bp.route('/my_events')
@login_required
def my_events():
    # Fetch all events created by this user
    events = Event.query.filter_by(creator_id=current_user.id).order_by(Event.date.desc()).all()
    return render_template('events/my_events.html', events=events)

@events_bp.route('/<id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    if event is None:
        flash("Event not found", "danger")
        return redirect(url_for('main.index'))
    # only the creator can update
    if event.creator != current_user:
        flash("You do not have permission to update this event", "danger")
        return redirect(url_for('event.show', id=event.id))
    # check if event is cancelled
    if event.status == "Cancelled":
      flash("This event has been cancelled and cannot be updated.", "warning")
      return redirect(url_for('event.show', id=event.id))
    
    form = EventUpdateForm()
    if form.validate_on_submit():
        # call the function that checks and returns image
        if form.image.data:
            db_file_path = check_upload_file(form)
            event.image = db_file_path
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
    if event is None:
        flash("Event not found", "danger")
        return redirect(url_for('event.my_events'))

    # only creator can cancel
    if event.creator != current_user:
        flash("You do not have permission to cancel this event", "danger")
        return redirect(url_for('event.show', id=event.id))

    event.cancel()  # sets status = "Cancelled"
    db.session.commit()

    flash("Event has been cancelled successfully.", "warning")
    return redirect(url_for('event.my_events'))
