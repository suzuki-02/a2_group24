from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, DateField, DecimalField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Email, EqualTo, NumberRange
from flask_wtf.file import FileRequired, FileField, FileAllowed, ValidationError

ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'png', 'jpg', 'jpeg'}

# creates the login information
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email("Please enter a valid email")])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

# this is the registration form
class RegisterForm(FlaskForm):
    first_name=StringField("First Name", validators=[InputRequired()])
    last_name=StringField("Last Name", validators=[InputRequired()])
    email = StringField("Email", validators=[Email("Please enter a valid email")])
    contact_number=StringField("Contact Number", validators=[InputRequired()])
    street_address=StringField("Street Address", validators=[InputRequired()])
    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(),
    EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")

    # submit button
    submit = SubmitField("Register")

# Create new event
class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[InputRequired()])
    date = DateField('Event Date', format='%Y-%m-%d', validators=[InputRequired()])
    price = DecimalField('Ticket Price ($)', places=2, validators=[
        InputRequired(), NumberRange(min=0, message="Price must be positive")
    ])
    quantity = IntegerField('Ticket Quantity', validators=[
        InputRequired(), NumberRange(min=1, message="At least 1 ticket required")
    ])
    description = TextAreaField('Description', validators=[InputRequired()])
    featuredevent = BooleanField('Make this a featured event')
    image = FileField('Event Image', validators=[
    FileRequired(message = 'Image cannot be empty'),
    FileAllowed(ALLOWED_FILE, message='Only supports png, jpg, JPG, PNG')])
    submit = SubmitField("Create")

# User comment
class CommentForm(FlaskForm):
    text = TextAreaField('Add your Comment', [InputRequired()])
    submit = SubmitField('Create')

# Purchase form
class PurchaseForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[
        InputRequired(message="Please enter the number of tickets"),
        NumberRange(min=1, message="You must purchase at least one ticket")
    ])
    submit = SubmitField('Purchase')

# Update event
class EventUpdateForm(FlaskForm):
    title = StringField('Event Title', validators=[InputRequired()])
    date = DateField('Event Date', format='%Y-%m-%d', validators=[InputRequired()])
    price = DecimalField('Ticket Price ($)', places=2, validators=[
        InputRequired(), NumberRange(min=0, message="Price must be positive")
    ])
    quantity = IntegerField('Ticket Quantity', validators=[
        InputRequired(), NumberRange(min=0, message="Ticket quantity cannot be negative")
    ])
    description = TextAreaField('Description', validators=[InputRequired()])
    image = FileField('Event Image', validators=[
    FileAllowed(ALLOWED_FILE, message='Only supports png, jpg, JPG, PNG')])
    submit = SubmitField("Update")