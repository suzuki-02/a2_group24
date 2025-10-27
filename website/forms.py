import re
from datetime import date
from flask import flash
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.fields import (
    TextAreaField, SubmitField, StringField, PasswordField,
    DateField, TimeField, DecimalField, IntegerField, BooleanField
)
from wtforms.validators import InputRequired, Email, EqualTo, NumberRange, ValidationError
from flask_wtf.file import FileField, FileAllowed
from wtforms.widgets import TimeInput


ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'png', 'jpg', 'jpeg'}


# -------------------
# Auth forms
# -------------------

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email("Please enter a valid email")])
    password = PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField("Email", validators=[Email("Please enter a valid email")])
    contact_number = StringField("Contact Number", validators=[InputRequired()])
    street_address = StringField("Street Address", validators=[InputRequired()])

    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            EqualTo('confirm', message="Passwords should match")
        ]
    )
    confirm = PasswordField("Confirm Password")
    submit = SubmitField("Register")

    # ---- Phone validation (AU mobile + landline) ----
    def validate_contact_number(self, field):
        raw = field.data or ""
        num = re.sub(r"[()\s-]+", "", raw)
        mobile_ok = re.fullmatch(r"04\d{8}", num) or re.fullmatch(r"\+614\d{8}", num)
        landline_ok = re.fullmatch(r"0[2378]\d{8}", num) or re.fullmatch(r"\+61[2378]\d{8}", num)
        if not (mobile_ok or landline_ok):
            raise ValidationError(
                "Enter a valid Australian phone number (e.g. 04XXXXXXXX, +614XXXXXXXX, 07XXXXXXXX, +617XXXXXXXX)."
            )

    # ---- Password complexity validation ----
    def validate_password(self, field):
        pw = field.data or ""
        min_len = 8
        if len(pw) < min_len:
            raise ValidationError(f"Password must be at least {min_len} characters long.")
        if re.search(r"\s", pw):
            raise ValidationError("Password must not contain spaces.")
        if not re.search(r"[A-Z]", pw):
            raise ValidationError("Password must include at least one uppercase letter (A–Z).")
        if not re.search(r"[a-z]", pw):
            raise ValidationError("Password must include at least one lowercase letter (a–z).")
        if not re.search(r"\d", pw):
            raise ValidationError("Password must include at least one digit (0–9).")
        if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:,.?/~`|\\]", pw):
            raise ValidationError("Password must include at least one special character (e.g. !@#$%).")
        common = {"password", "letmein", "qwerty", "abc123", "12345678", "iloveyou"}
        if pw.lower() in common:
            raise ValidationError("That password is too common. Please choose a stronger one.")


# -------------------
# Event form
# -------------------

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[InputRequired()])
    date = DateField('Event Date', format='%Y-%m-%d', validators=[InputRequired()])
    venue = StringField('Venue', validators=[InputRequired()])

    genre = SelectField(
        'Genre',
        choices=[
            ('Rock', 'Rock'),
            ('Jazz', 'Jazz'),
            ('Pop', 'Pop'),
            ('Hip Hop', 'Hip Hop'),
            ('Electronic', 'Electronic'),
            ('Classical', 'Classical')
        ],
        validators=[InputRequired()]
    )

    # Times
    start_time = TimeField('Start Time', format='%H:%M',
                        validators=[InputRequired()], widget=TimeInput())
    door_time = TimeField('Door Time', format='%H:%M',
                        validators=[InputRequired()], widget=TimeInput())

    price = DecimalField('Ticket Price ($)', places=2, validators=[
        InputRequired(), NumberRange(min=0, message="Price must be positive")
    ])
    quantity = IntegerField('Ticket Quantity', validators=[
        InputRequired(), NumberRange(min=1, message="At least 1 ticket required")
    ])
    description = TextAreaField('Description', validators=[InputRequired()])
    featuredevent = BooleanField('Make this a featured event')

    image = FileField('Event Image', validators=[
        FileAllowed(ALLOWED_FILE, message='Only supports png, jpg, JPG, PNG')
    ])

    submit = SubmitField("Create")

    # ---- Custom field validations ----
    def validate_door_time(self, field):
        if self.start_time.data and field.data and field.data > self.start_time.data:
            raise ValidationError("Door time must be before the start time.")

    def validate_date(self, field):
        """Prevent creating events in the past."""
        if field.data and field.data < date.today():
            flash("You cannot create an event in the past.", "danger")
            raise ValidationError("Event date cannot be in the past.")


# -------------------
# Other forms
# -------------------

class CommentForm(FlaskForm):
    text = TextAreaField('Add your Comment', [InputRequired()])
    submit = SubmitField('Create')


class PurchaseForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[
        InputRequired(message="Please enter the number of tickets"),
        NumberRange(min=1, message="You must purchase at least one ticket")
    ])
    submit = SubmitField('Purchase')


class EventUpdateForm(FlaskForm):
    title = StringField('Event Title', validators=[InputRequired()])
    venue = StringField('Venue', validators=[InputRequired()])
    date = DateField('Event Date', format='%Y-%m-%d', validators=[InputRequired()])

    genre = SelectField(
        'Genre',
        choices=[
            ('House', 'House'),
            ('Rock', 'Rock'),
            ('Jazz', 'Jazz'),
            ('Pop', 'Pop'),
            ('Hip Hop', 'Hip Hop'),
            ('R&B', 'R&B'),
            ('Electronic', 'Electronic'),
            ('Classical', 'Classical')
        ],
        validators=[InputRequired()]
    )

    # Times
    start_time = TimeField('Start Time', format='%H:%M',
                        validators=[InputRequired()], widget=TimeInput())
    door_time = TimeField('Door Time', format='%H:%M',
                        validators=[InputRequired()], widget=TimeInput())

    price = DecimalField('Ticket Price ($)', places=2, validators=[
        InputRequired(), NumberRange(min=0, message="Price must be positive")
    ])
    quantity = IntegerField('Ticket Quantity', validators=[
        InputRequired(), NumberRange(min=0, message="Ticket quantity cannot be negative")
    ])
    description = TextAreaField('Description', validators=[InputRequired()])
    featuredevent = BooleanField('Make this a featured event')
    image = FileField('Event Image', validators=[
        FileAllowed(ALLOWED_FILE, message='Only supports png, jpg, JPG, PNG')
    ])
    submit = SubmitField("Update")
