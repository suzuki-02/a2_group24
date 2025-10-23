from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users' # good practice to specify table name
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), index=True, nullable=False)
    last_name = db.Column(db.String(50), index=True, nullable=False)
    email = db.Column(db.String(100), index=True, unique=True, nullable=False)
    contact_number = db.Column(db.String(20))
    street_address = db.Column(db.String(200))
	# password should never stored in the DB, an encrypted password is stored
	# the storage should be at least 255 chars long, depending on your hashing algorithm
    password_hash = db.Column(db.String(255), nullable=False)
    # relation to call user.comments and comment.created_by
    comments = db.relationship('Comment', backref='user')
    # relation to call user.events and event.creator
    events = db.relationship('Event', backref='creator')
    
    # string print method
    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    venue = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    door_time = db.Column(db.Time, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    image = db.Column(db.String(400))

    # Event state (Open, Inactive, Sold Out, Cancelled)
    status = db.Column(db.String(20), nullable=False, default="Open")

    # ... Create the Comments db.relationship
	# relation to call event.comments and comment.event
    comments = db.relationship('Comment', backref='event')

    # add the foreign key to link to User (event creator)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # update event status based on date and ticket availability
    def update_status(self):
        if self.status == "Cancelled":
            return  # don't override status if it is cancelled
        
        today = datetime.now().date()
        
        if self.date < today:
            self.status = "Inactive"
        elif self.quantity <= 0:
            self.status = "Sold Out"
        else:
            self.status = "Open"
    
    # cancel event manually TODO: only by creator
    def cancel(self):
        self.status = "Cancelled"
	
    # string print method
    def __repr__(self):
        return f"Event title: {self.title}"

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    # add the foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    # string print method
    def __repr__(self):
        return f"Comment: {self.text}"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    # add the foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    # relationship to Event and User
    event = db.relationship('Event', backref='orders')
    user = db.relationship('User', backref='orders')

    # calculate total price
    def calculate_total(self):
        """Calculate total based on event.price * quantity."""
        if self.event and self.quantity:
            self.total_price = float(self.event.price) * self.quantity