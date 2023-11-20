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
        # Checking for ASCII characters
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
        if not not re.search("^-|-$", domain):
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


def check_name(name: str):
    if not not re.search("[*?!'^+%&/()=}\]\[{$#@<>]", name):
        return None
    return name.strip()

def check_phone(phone: str):
    # Remove whitespace and dashes
    # phone = phone.replace(" ", "")
    # phone = phone.replace("-", "")

    if not re.search("^[0-9]{4}-[0-9]{3}-[0-9]{4}$", phone):
        return None
    return phone


def check_password(password: str):

    # Checks for digit, lowercase, uppercase, special character
    if not re.search("[0-9]", password):
        return None
    if not re.search("[a-z]", password):
        return None
    if not re.search("[A-Z]", password):
        return None
    if not re.search("[^a-zA-Z\d\s]", password):
        return None

    # Return none if it contains whitespace
    if not not re.search("\s", password):
        return None

    if len(password) < 6 or len(password) > 12:
        return None

    return password


def verify_password(password, confirm):
    return password == confirm

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

        # Checking user input
        email = check_email(form.email.data)
        first_name = check_name(form.email.data)
        last_name = check_name(form.email.data)
        phone = check_phone(form.email.data)
        password = check_password(form.email.data)
        pass_verify = verify_password(form.password.data, form.confirm_password.data)

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
            flash("Phone number invalid (XXXX-XXX-XXXX)")
            return render_template('users/register.html', form=form)
        if not password:
            flash("Password invalid, must be between 6-12 characters long, contain uppercase, lowercase, number and "
                  "special character")
            return render_template('users/register.html', form=form)
        if not pass_verify:
            flash("Passwords don't match")
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
    print(check_email("123@gm.123x-xx"))
    print(check_name("Hey"))
    print(check_name("Seb "))
    print(check_phone("0772-199 1238"))
    print(check_password("123abcABC@@"))
