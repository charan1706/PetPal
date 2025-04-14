


from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed

class PetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

    pet_type = SelectField(
        'Type',
        choices=[
            ('Dog', 'Dog'),
            ('Cat', 'Cat'),
            ('Bird', 'Bird'),
            ('Rabbit', 'Rabbit'),
            ('Other', 'Other')
        ],
        validators=[DataRequired()]
    )

    breed = SelectField('Breed', choices=[], validators=[DataRequired()])

    age_years = IntegerField('Age (Years)', default=0, validators=[NumberRange(min=0)])
    age_months = IntegerField('Age (Months)', default=0, validators=[NumberRange(min=0, max=11)])

    price = FloatField('Price ($)', validators=[DataRequired()])

    image = FileField('Pet Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])

    submit = SubmitField('Add Pet')
