# IMPORTS
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_qrcode import QRcode
from flask_login import current_user
import os
from dotenv import load_dotenv
from functools import wraps
import logging
from flask_talisman import Talisman


# Get our filter, we only want messages that include the word SECURITY
class SecurityFilter(logging.Filter):
    def filter(self, record):
        return 'SECURITY' in record.getMessage()


# Our general logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File handler for saving into lottery.log
file_handler = logging.FileHandler('lottery.log', 'a')
file_handler.setLevel(logging.WARNING)
file_handler.addFilter(SecurityFilter())

# How we want our logs formatted
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)

# Adding our filehandler to our logger
logger.addHandler(file_handler)

# Load up our .env file
load_dotenv()

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ECHO'] = os.environ.get('SQLALCHEMY_ECHO')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY')


def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            #  Checks if the user is anonymous
            if not current_user.is_authenticated:
                # Checks if function is made for anonymous users/If anonymous isn't allowed we send them
                # back to the login page
                if 'anonymous' not in roles:
                    flash('Please log in to access this page')
                    return redirect(url_for('users.login'))
            # If the user isn't allowed to access the page, we send him to the 403 Forbidden Error page
            elif current_user.role not in roles:

                # Add a log that a user with ID ... email ... role ... and IP ... has tried accessing an
                # unauthorized page
                logging.warning('SECURITY - Unauthorized Access Attempt [%s, %s, %s, %s]',
                                current_user.id,
                                current_user.email,
                                current_user.role,
                                request.remote_addr
                                )

                return render_template('errors/403.html')

            return f(*args, **kwargs)

        return wrapped

    return wrapper


# initialise database
db = SQLAlchemy(app)

# Create our security headers
csp = {'default-src': [
        '\'self\'',
        'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css'
    ],
    'frame-src': [
        '\'self\'',
        'https://www.google.com/recaptcha/',
        'https://recaptcha.google.com/recaptcha/'
    ],
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'https://www.google.com/recaptcha/',
        'https://www.gstatic.com/recaptcha/'],
    'img-src': [
        'data:'
    ]}
talisman = Talisman(app, content_security_policy=csp)

# Initialize QR Code
qrcode = QRcode(app)


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('main/index.html')


# BLUEPRINTS
# import blueprints
from users.views import users_blueprint
from admin.views import admin_blueprint
from lottery.views import lottery_blueprint

#
# # register blueprints with app
app.register_blueprint(users_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(lottery_blueprint)

# Login Manager
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.init_app(app)

from models import User


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# Error handling for Errors: 400,403,404,500,503
@app.errorhandler(400)
def bad_request(error):
    return render_template('errors/400.html'), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 404


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 404


@app.errorhandler(503)
def service_unavailable(error):
    return render_template('errors/503.html'), 404


if __name__ == "__main__":
    # Run it as HTTPS
    app.run(ssl_context=('cert.pem', 'key.pem'))
