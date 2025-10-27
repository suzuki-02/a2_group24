from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])

def login():
    login_form = LoginForm()
    error = None
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.email==email))
        #if there is no user with that name
        if user is None:
            error = 'Incorrect email'
        elif not check_password_hash(user.password_hash, password):
            error = 'Incorrect password'
        if error is None:
            #all good, set the login_user of flask_login to manage the user
            login_user(user)
            nextp = request.args.get('next')
            print(nextp)
            if nextp is None or not nextp.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(nextp)
        else:
            flash(error, 'danger')
    return render_template('user.html', form=login_form, heading='Login')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        # Check if email already exists
        existing_user = db.session.scalar(db.select(User).where(User.email == register_form.email.data))
        if existing_user:
            flash("That email is already registered. Please log in instead.", "warning")
            return redirect(url_for("auth.login"))
        
        # Otherwise, create new user
        user = User(
            first_name = register_form.first_name.data,
            last_name = register_form.last_name.data,
            contact_number = register_form.contact_number.data,
            street_address = register_form.street_address.data,
            email = register_form.email.data,
            password_hash = generate_password_hash(register_form.password.data)
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('user.html', form=register_form, heading='Register')
