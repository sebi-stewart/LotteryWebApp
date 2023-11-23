from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField


class RegisterForm(FlaskForm):
    email = StringField()
    firstname = StringField()
    lastname = StringField()
    phone = StringField()
    password = PasswordField()
    confirm_password = PasswordField()
    date_of_birth = StringField()
    postcode = StringField()
    submit = SubmitField()


# Login Form for login page
class LoginForm(FlaskForm):
    email = StringField()
    password = PasswordField()
    captcha_pin = StringField()
    reCaptcha = StringField()
    submit = SubmitField()