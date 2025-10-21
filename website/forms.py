import re
from flask_wtf import FlaskForm
from wtforms.fields import (
    TextAreaField, SubmitField, StringField, PasswordField,
    DateField, DecimalField, IntegerField, TimeField
)
from wtforms.widgets import TimeInput
from wtforms.validators import InputRequired, Email, EqualTo, NumberRange, ValidationError
from flask_wtf.file import FileRequired, FileField, FileAllowed

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
    last_name  = StringField("Last Name", validators=[InputRequired()])
    email = StringField("Email", validators=[Email("Please enter a valid email")])
    contact_number = StringField("Contact Number", validators=[InputRequired()])
    street_address = StringField("Street Address", validators=[InputRequired()])

    # Password + confirm (EqualTo already present)
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

        # RULES (tweak as needed):
        min_len = 8
        require_upper = True
        require_lower = True
        require_digit = True
        require_special = True
        disallow_spaces = True

        if len(pw) < min_len:
            raise ValidationError(f"Password must be at least {min_len} characters long.")

        if disallow_spaces and re.search(r"\s", pw):
            raise ValidationError("Password must not contain spaces.")

        if require_upper and not re.search(r"[A-Z]", pw):
            raise ValidationError("Password must include at least one uppercase letter (A–Z).")

        if require_lower and not re.search(r"[a-z]", pw):
            raise ValidationError("Password must include at least one lowercase letter (a–z).")

        if require_digit and not re.search(r"\d", pw):
            raise ValidationError("Password must include at least one digit (0–9).")

        # You can adjust the special set if your policy differs
        if require_special and not re.search(r"[!@#$%^&*()_\-+=\[\]{};:,.?/~`|\\]", pw):
            raise ValidationError("Password must include at least one special character (e.g. !@#$%).")

        # (Optional) block very common passwords even if they meet rules
        common = {"password", "letmein", "qwerty", "abc123", "12345678", "iloveyou"}
        if pw.lower() in common:
            raise ValidationError("That password is too common. Please choose a stronger one.")


# -------------------
# Event form
# -------------------

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[InputRequired()])
    date = DateField('Event Date', format='%Y-%m-%d', validators=[InputRequired()])

    # Times (HTML5 time inputs)
    start_time = TimeField('Start Time', format='%H:%M',
                           validators=[InputRequired()], widget=TimeInput())
    door_time  = TimeField('Door Time',  format='%H:%M',
                           validators=[InputRequired()], widget=TimeInput())

    price = DecimalField('Ticket Price ($)', places=2, validators=[
        InputRequired(), NumberRange(min=0, message="Price must be positive")
    ])
    quantity = IntegerField('Ticket Quantity', validators=[
        InputRequired(), NumberRange(min=1, message="At least 1 ticket required")
    ])
    description = TextAreaField('Description', validators=[InputRequired()])
    image = FileField('Event Image', validators=[
        FileRequired(message='Image cannot be empty'),
        FileAllowed(ALLOWED_FILE, message='Only supports png, jpg, JPG, PNG')
    ])
    submit = SubmitField("Create")

    def validate_door_time(self, field):
        if self.start_time.data and field.data and field.data > self.start_time.data:
            raise ValidationError("Door time must be before the start time.")


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
<<<<<<< HEAD

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
=======
>>>>>>> Haris-first-branch
