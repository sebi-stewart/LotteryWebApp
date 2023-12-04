from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange, InputRequired


class DrawForm(FlaskForm):
    number1 = IntegerField(id='no1', validators=[
        InputRequired(message='No. 1 required'),
        NumberRange(min=1, max=60)
    ])
    number2 = IntegerField(id='no2', validators=[
        InputRequired('No. 2 required'),
        NumberRange(min=1, max=60)
    ])
    number3 = IntegerField(id='no3', validators=[
        InputRequired('No. 3 required'),
        NumberRange(min=1, max=60)
    ])
    number4 = IntegerField(id='no4', validators=[
        InputRequired('No. 4 required'),
        NumberRange(min=1, max=60)
    ])
    number5 = IntegerField(id='no5', validators=[
        InputRequired('No. 5 required'),
        NumberRange(min=1, max=60)
    ])
    number6 = IntegerField(id='no6', validators=[
        InputRequired('No. 6 required'),
        NumberRange(min=1, max=60)
    ])
    submit = SubmitField("Submit Draw")
