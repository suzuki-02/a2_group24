from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField
from wtforms.validators import InputRequired, Email, EqualTo
from flask_wtf.file import FileRequired, FileField, FileAllowed

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
    description = TextAreaField('Description', validators=[InputRequired()])
    image = FileField('Event Image', validators=[
    FileRequired(message = 'Image cannot be empty'),
    FileAllowed(ALLOWED_FILE, message='Only supports png, jpg, JPG, PNG')])
    submit = SubmitField("Create")

# User comment
class CommentForm(FlaskForm):
    text = TextAreaField('Comment', [InputRequired()])
    submit = SubmitField('Create')