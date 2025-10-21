from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
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
<<<<<<< HEAD
            error = 'Incorrect email'
        elif not check_password_hash(user.password_hash, password):
=======
            error = 'Incorrect username'#could be a security risk to give this much info away
        #check the password - notice password hash function
        elif not check_password_hash(user.password_hash, password): # takes the hash and password
>>>>>>> 0303ac17aa487cd334720c5a28559ebbb3d9038c
            error = 'Incorrect password'
        if error is None:
            #all good, set the login_user of flask_login to manage the user
            login_user(user)
<<<<<<< HEAD
            nextp = request.args.get('next')
            print(nextp)
            if nextp is None or not nextp.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(nextp)
=======
            return redirect(url_for('main.index'))
>>>>>>> 0303ac17aa487cd334720c5a28559ebbb3d9038c
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
<<<<<<< HEAD
        user = User(
            first_name = register_form.first_name.data,
            last_name = register_form.last_name.data,
            contact_number = register_form.contact_number.data,
            street_address = register_form.street_address.data,
            email = register_form.email.data,
            password_hash = generate_password_hash(register_form.password.data)
        )
        
        db.session.add(user)
=======
        #get user info from the form
        first_name = register_form.first_name.data
        last_name = register_form.last_name.data
        contact_number = register_form.contact_number.data
        street_address = register_form.street_address.data
        email = register_form.email.data
        password_hash = generate_password_hash(register_form.password.data)  # don't store the password in plaintext!
        #check if a user exists with the email
        user = db.session.scalar(db.select(User).where(User.email==email))
        if user:#this returns true when user is not None
            flash('Email already exists, please try another', 'danger')
            return redirect(url_for('auth.register'))
        #create a new User model object
        new_user = User(first_name=first_name, last_name=last_name, contact_number=contact_number, street_address=street_address, email=email, password_hash=password_hash)
        # add the object to the db session
        db.session.add(new_user)
        # commit to the database
>>>>>>> 0303ac17aa487cd334720c5a28559ebbb3d9038c
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('user.html', form=register_form, heading='Register')