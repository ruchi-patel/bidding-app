from flask_wtf import FlaskForm
from wtforms.fields import (StringField, SelectField)
from wtforms.validators import DataRequired
from .choices import *

class PaymentForm(FlaskForm):
    name = StringField('Payment Nickname', validators=[DataRequired()])
    payment_type = SelectField('Payment Type', validators=[DataRequired()])
    name_on_card = StringField('Name of the card', validators=[DataRequired()])
    card_number = StringField('Card Number', validators=[DataRequired()])
    year = SelectField('Year', choices=years, validators=[DataRequired()])
    month = SelectField('Month', choices=months, validators=[DataRequired()])



