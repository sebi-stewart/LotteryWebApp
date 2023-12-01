import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError, Length, EqualTo


class RegisterForm(FlaskForm):
    email = StringField(label='Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid Email format')
    ])

    firstname = StringField(label='First Name', validators=[
        DataRequired(message='First Name is required')
    ])

    lastname = StringField(label='Last Name', validators=[
        DataRequired(message='Last Name is required')
    ])

    phone = StringField(label='Phone', validators=[
        DataRequired(message='Phone is required')
    ])

    password = PasswordField(label='Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, max=12, message='Password must be between 6 and 12 characters long')
    ])

    confirm_password = PasswordField(label='Confirm Password', validators=[
        DataRequired(message='Confirm Password is required'),
        EqualTo('password', message='Both password fields must be equal')
    ])

    date_of_birth = StringField(label='Date of Birth', validators=[
        DataRequired(message='Date of Birth is required')
    ])

    postcode = StringField(label='Postcode', validators=[
        DataRequired(message='Postcode is required')
    ])

    submit = SubmitField(label='Submit')

    def validate_firstname(self, firstname):
        pattern = re.compile("[^*?!'^+%&/()=}\]\[{$#@<>]")
        if not pattern.match(firstname.data):
            raise ValidationError('First Name cannot contain special characters')

    def validate_lastname(self, lastname):
        pattern = re.compile("[^*?!'^+%&/()=}\]\[{$#@<>]")
        if not pattern.match(lastname.data):
            raise ValidationError('First Name cannot contain special characters')

    def validate_phone(self, phone):
        pattern = re.compile("^[0-9]{4}-[0-9]{3}-[0-9]{4}$")
        if not pattern.match(phone.data):
            raise ValidationError('Phone number invalid, must be in format XXXX-XXX-XXXX')

    def validate_password(self, password):
        # Checks for digit, lowercase, uppercase, special character
        mistakes = []
        error = False

        if not re.search("[0-9]", password.data):
            mistakes.append("a number")
            error = True
        if not re.search("[a-z]", password.data):
            mistakes.append("a lowercase letter")
            error = True
        if not re.search("[A-Z]", password.data):
            mistakes.append("an uppercase letter")
            error = True
        if not re.search("[^a-zA-Z\d\s]", password.data):
            mistakes.append("a special character")
            error = True
        # Return none if it contains whitespace
        if not not re.search("\s", password.data):
            raise ValidationError("Password invalid, must not contain whitespace")

        output_message = ", ".join(mistakes)

        if error:
            raise ValidationError("Password invalid, must contain " + output_message)

    def validate_date_of_birth(self, date_of_birth):
        # Checks format
        if not re.search('^(0[1-9]|[1-2][0-9]|3[0-1])/(0[1-9]|1[0-2])/\d{4}$', date_of_birth.data):
            raise ValidationError('Date of birth invalid, must be in format DD/MM/YYYY')

    def validate_postcode(self, postcode):
        error = False
        # Checks format
        if not not re.search('(^[A-Z]{1}[0-9]{1} [0-9]{1}[A-Z]{2}$)', postcode.data):
            error = True

        # Check for the format 2
        if not not re.search('(^[A-Z]{1}[0-9]{2} [0-9]{1}[A-Z]{2}$)', postcode.data):
            error = True

        # Check for the format 3
        if not not re.search('(^[A-Z]{2}[0-9]{1} [0-9]{1}[A-Z]{2}$)', postcode.data):
            error = True

        if error:
            raise ValidationError("Postcode invalid, must be in format 'XY YXX', 'XYY YXX' or 'XXY YXX' "
                                  "(X=Letter, Y=Number)")


# Login Form for login page
class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[
        DataRequired(message='Email is required')
    ])
    password = PasswordField(label='Password', validators=[
        DataRequired(message='Password is required')
    ])
    captcha_pin = StringField()
    reCaptcha = StringField()
    submit = SubmitField()

