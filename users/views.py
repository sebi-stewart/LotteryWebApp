# IMPORTS
import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_user, current_user
from app import db
from models import User
from users.forms import RegisterForm, LoginForm
from users.data_checks import *


# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')



# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # Checking user input
        email = check_email(form.email.data)
        first_name = check_name(form.firstname.data)
        last_name = check_name(form.lastname.data)
        phone = check_phone(form.phone.data)
        password = check_password(form.password.data)
        pass_verify = verify_password(form.password.data, form.confirm_password.data)
        date_of_birth = check_date_of_birth(form.date_of_birth.data)
        postcode = check_postcode(form.postcode.data)

        # Notifying user if their input was invalid
        if not email:
            flash("Email address invalid")
            return render_template('users/register.html', form=form)
        if not first_name:
            flash("First name invalid")
            return render_template('users/register.html', form=form)
        if not last_name:
            flash("Last name invalid")
            return render_template('users/register.html', form=form)
        if not phone:
            flash("Phone number invalid, must be in format XXXX-XXX-XXXX")
            return render_template('users/register.html', form=form)
        if not password:
            flash("Password invalid, must be between 6-12 characters long, contain uppercase, lowercase, number and "
                  "special character")
            return render_template('users/register.html', form=form)
        if not pass_verify:
            flash("Passwords don't match")
            return render_template('users/register.html', form=form)
        if not date_of_birth:
            flash("Date of birth invalid, must be in format DD/MM/YYYY")
            return render_template('users/register.html', form=form)
        if not postcode:
            flash("Postcode invalid, must be in format 'XY YXX', 'XYY YXX' or 'XXY YXX'")
            return render_template('users/register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user',
                        pin_key=pyotp.random_base32(),
                        date_of_birth=form.date_of_birth.data,
                        postcode=form.postcode.data)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Adding the current users email to the session
        session['username'] = new_user.email

        # sends user to login page
        return redirect(url_for('users.setup_2fa'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


@users_blueprint.route('/setup_2fa')
def setup_2fa():
    # Checking if the user/email is in session
    if 'username' not in session:
        return redirect('/')

    # Check if the
    user = User.query.filter_by(email=session['username']).first()
    if not user:
        return redirect('/')

    del session['username']

    return (render_template('users/setup_2fa.html', username=user.email, uri=user.get_2fa_uri()),
            200, {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            })


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # Creating login form
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if email or password doesn't exist, we output the same message
        if not user or not user.verify_password(form.password.data):
            flash("Email or Password doesn't exist")
            return render_template('users/login.html', form=form)

        login_user(user)

        return redirect(url_for('users.account'))

    return render_template('users/login.html', form=form)


# view user account
@users_blueprint.route('/account')
def account():
    if current_user.is_anonymous:
        return render_template('users/account.html',
                               acc_no="PLACEHOLDER FOR USER ID",
                               email="PLACEHOLDER FOR USER EMAIL",
                               firstname="PLACEHOLDER FOR USER FIRSTNAME",
                               lastname="PLACEHOLDER FOR USER LASTNAME",
                               phone="PLACEHOLDER FOR USER PHONE")
    return render_template('users/account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)


