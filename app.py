# IMPORTS
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_qrcode import QRcode
import os
from dotenv import load_dotenv


load_dotenv()

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LONG AND SECRET KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY')

# initialise database
db = SQLAlchemy(app)

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

    app.run()
