from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

# Create a blueprint - make sure all BPs have unique names
auth_bp = Blueprint('auth', __name__)

# this is a hint for a login function
@auth_bp.route('/login', methods=['GET', 'POST'])
# view function
def login():
    login_form = LoginForm()
    error = None
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.email==email))
        if user is None:
            error = 'Incorrect email'
        elif not check_password_hash(user.password_hash, password): # takes the hash and cleartext password
            error = 'Incorrect password'
        if error is None:
            login_user(user)
            nextp = request.args.get('next') # this gives the url from where the login page was accessed
            print(nextp)
            if nextp is None or not nextp.startswith('/'):
                return redirect(url_for('main.index')) # change to the page you want
            return redirect(nextp)
        else:
            flash(error)
    return render_template('user.html', form=login_form, heading='Login')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user() # will remove the user id from the session
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User(
            first_name = register_form.first_name.data,
            last_name = register_form.last_name.data,
            contact_number = register_form.contact_number.data,
            street_address = register_form.street_address.data,
            email = register_form.email.data,
            password_hash = generate_password_hash(register_form.password.data)
        )
        # add the object to the db session
        db.session.add(user)
        # commit to the database
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('user.html', form=register_form, heading='Register')