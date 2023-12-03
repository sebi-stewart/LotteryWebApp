# IMPORTS
import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from flask_login import login_user, current_user, logout_user
from app import db, required_roles
from models import User
from users.forms import RegisterForm, LoginForm, ChangePasswordForm
from markupsafe import Markup
from datetime import datetime
import logging

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS

# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
@required_roles('anonymous', 'admin')
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

        # Check if we are logged in (as admin) or if we are anonymous
        # If we don't do the first check and only use current_user.rol, it would throw an error if the user is anonymous
        if not current_user.is_authenticated:
            role = 'user'
        elif current_user.role == 'admin':
            role = 'admin'
        else:
            role = 'user'

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role=role,
                        pin_key=pyotp.random_base32(),
                        date_of_birth=form.date_of_birth.data,
                        postcode=form.postcode.data)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Add a log that a user with email ... and ip ... was registered
        logging.warning('SECURITY - User registration [%s, %s]',
                        form.email.data,
                        request.remote_addr
                        )

        # Adding the current users email to the session
        session['username'] = new_user.email

        # sends user to 2FA page
        if new_user.role == 'user':
            return redirect(url_for('users.setup_2fa'))
        elif new_user.role == 'admin':
            flash(f'A new Admin User ({new_user.lastname}, {new_user.firstname}) has been registered successfully!')
            return redirect(url_for('admin.admin'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


@users_blueprint.route('/setup_2fa')
@required_roles('anonymous')
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


# Log invalid login attempts
@required_roles('anonymous')
def invalid_login(user: str):
    # Add a log that a user with  Email ... (from form) and IP ... has unsuccessfully tried to log in
    logging.warning('SECURITY - Invalid login attempt [%s, %s]',
                    user,
                    request.remote_addr
                    )
    pass


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
@required_roles('anonymous')
def login():
    # Checking amount of login attempts
    if not session.get('attempts'):
        # Login attempts
        session['attempts'] = 0

    # Creating login form
    form = LoginForm()

    if form.validate_on_submit():
        # Make sure they cannot log in if they have already submitted 3 wrong answers
        if session['attempts'] > 3:

            # Log this attempt, even though we don't let him log in because the user exceeded the max amount we still
            # want make sure that this attempt is logged
            invalid_login(form.email.data)

            flash(Markup('Number of incorrect login attempts exceeded. '
                         'Please click <a href="/reset">here</a> to reset.'))
            return render_template('users/login.html', form=form)

        user = User.query.filter_by(email=form.email.data).first()

        # if email or password doesn't exist, we output the same message
        if (not user
                or not user.verify_postcode(form.postcode.data)
                or not user.verify_password(form.password.data)
                or not user.verify_pin(form.pin.data)):
            session['attempts'] += 1

            # If the data was input incorrect/doesn't match the database, we log the invalid attempt
            invalid_login(form.email.data)

            # Check if login attempts have been exceeded
            # Same code as above but makes the reset code show earlier instead of 0 attempts remaining
            if session['attempts'] >= 3:
                flash(Markup('Number of incorrect login attempts exceeded. '
                             'Please click <a href="/reset">here</a> to reset.'))
                return render_template('users/login.html', form=form)

            flash('Please check your login details and try again, '
                  '{} login attempts remaining'.format(3 - session.get('attempts')))
            return render_template('users/login.html', form=form)

        # Log in the user and reset our login attempts
        login_user(user)
        session['attempts'] = 0

        # Update our current/last login variables
        current_user.last_login = current_user.current_login
        current_user.current_login = datetime.now()
        db.session.commit()

        # Add a log that a user with ID ... email ... and IP ... has logged in
        logging.warning('SECURITY - Log in [%s, %s, %s]',
                        current_user.id,
                        current_user.email,
                        request.remote_addr
                        )

        # Check which page he should be redirected to
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin'))
        elif current_user.role == 'user':
            return redirect(url_for('lottery.lottery'))
        else:
            return redirect(url_for('users.account'))

    return render_template('users/login.html', form=form)


@users_blueprint.route('/reset')
@required_roles('anonymous')
def reset():
    session['attempts'] = 0
    return redirect(url_for('users.login'))


@users_blueprint.route('/logout')
@required_roles('user', 'admin')
def logout():
    logout_user()

    # Add a log that a user with Email ... and IP ... has logged out
    logging.warning('SECURITY - Log out [%s, %s]',
                    current_user.email,
                    request.remote_addr
                    )

    return redirect(url_for('index'))


# view user account
@users_blueprint.route('/account')
@required_roles('user', 'admin')
def account():
    return render_template('users/account.html')


@users_blueprint.route('/change_password', methods=['GET', 'POST'])
@required_roles('user', 'admin')
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Make sure the current password matches the database
        if current_user.verify_password(form.current_password.data):
            # We already check if the current password matches the new one via the form

            current_user.password = form.new_password.data
            db.session.commit()
            flash('Password changed successfully')

            return redirect(url_for('users.account'))

        flash('Current Password was Incorrect')

    return render_template('users/change_password.html', form=form)
