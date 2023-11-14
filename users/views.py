# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for
from app import db
from models import User
from users.forms import RegisterForm
import re

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')

# Valid Email address format as per Wikipedia's requirements https://en.wikipedia.org/wiki/Email_address
def check_email(email: str):
    email = email.lower().strip()

    if not not re.search("\s+", email):
        return None

    try:
        local_part, domain = email.split("@")

        if not local_part or not domain:
            return None

        # Checking local_part
        # Checking for ASCI characters
        for letter in local_part:
            if ((not re.search("\w", letter)) and
                    (not re.search("[!#$%&'*+-/=?^_`{|}~.]", letter))):
                return None

        # Checking there isn't double . or starts/ends with .
        if ((not not re.search("^[.]|[.]$", local_part)) or
                (not not re.search("[.]{2}", local_part))):
            return None

        # Checking domain
        # Checking latin letters
        if not re.search("[a-z]+", domain):
            return None

        # Checking there isn't double . or starts/ends with .
        if ((not not re.search("^[.]|[.]$", domain)) or
                (not not re.search("[.]{2}", domain))):
            return None

        # Checking there isn't double . or starts/ends with .
        if not not re.search("^[-]|[-]$", domain):
            return None

        # Remove hyphens and dots to stop false trigger on non word line
        domain = domain.replace(".", "")
        domain = domain.replace("-", "")

        # Checking for non word characters including underscore _
        if ((not not re.search("\W", domain)) or
            (not not re.search("_", domain))):
            return None

        return email

    except ValueError as er:
        print(er)
        return None


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    print("Hello")
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
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


# view user login
@users_blueprint.route('/login')
def login():
    return render_template('users/login.html')


# view user account
@users_blueprint.route('/account')
def account():
    return render_template('users/account.html',
                           acc_no="PLACEHOLDER FOR USER ID",
                           email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME",
                           lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")


if __name__ == "__main__":
    print(check_email("seb!1238s-.as@gm.123x-xx"))
