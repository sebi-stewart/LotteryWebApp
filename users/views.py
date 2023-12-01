# IMPORTS
import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_user, current_user, logout_user
from app import db
from models import User
from users.forms import RegisterForm, LoginForm
from markupsafe import Markup

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

    if not session.get('attempts'):
        # Login attempts
        session['attempts'] = 0

    form = LoginForm()

    if form.validate_on_submit():
        # Check if login attempts have been exceeded
        if session['attempts'] >= 3:
            flash(Markup('Number of incorrect login attempts exceeded. '
                         'Please click <a href="/reset">here</a> to reset.'))
            return render_template('users/login.html', form=form)

        user = User.query.filter_by(email=form.email.data).first()

        # if email or password doesn't exist, we output the same message
        if (not user
                or not user.verify_password(form.password.data)
                or not user.verify_pin(form.pin.data)):
            session['attempts'] += 1

            # Check if login attempts have been exceeded
            if session['attempts'] >= 3:
                flash(Markup('Number of incorrect login attempts exceeded. '
                             'Please click <a href="/reset">here</a> to reset.'))
                return render_template('users/login.html', form=form)

            flash('Please check your login details and try again, '
                  '{} login attempts remaining'.format(3 - session.get('attempts')))
            return render_template('users/login.html', form=form)

        session['attempts'] = 0
        login_user(user)

        return redirect(url_for('users.account'))

    return render_template('users/login.html', form=form)

@users_blueprint.route('/reset')
def reset():
    session['attempts'] = 0
    return redirect(url_for('users.login'))

@users_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


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
