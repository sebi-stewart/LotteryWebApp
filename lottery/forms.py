from flask import flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange, InputRequired, ValidationError


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

    def validate(self, **kwargs):
        standard_validators = FlaskForm.validate(self)
        if standard_validators:
            numbers = [self.number1.data, self.number2.data, self.number3.data,
                       self.number4.data, self.number5.data, self.number6.data]
            checker = {}

            for num in numbers:
                print(not checker.get(num))
                if not checker.get(num):
                    checker[num] = 1
                else:
                    flash('All numbers must be unique!')
                    return False

            last_num = 0
            for current_num in numbers:
                if current_num < last_num:
                    flash('The numbers must be in ascending order!')
                    return False
                last_num = current_num

            return True
        return False
