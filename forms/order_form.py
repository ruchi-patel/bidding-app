from flask_wtf import FlaskForm
from wtforms.fields import (StringField, SelectField)
from wtforms.validators import DataRequired

from .choices import *

class OrderForm(FlaskForm):
    # Payment details
    payment_name = StringField('Payment Nickname', validators=[DataRequired()])
    payment_type = SelectField('Payment Type', choices=payment_types, validators=[DataRequired()])
    name_on_card = StringField('Name of the card', validators=[DataRequired()])
    card_number = StringField('Card Number', validators=[DataRequired()])
    year = SelectField('Year', choices=years, validators=[DataRequired()])
    month = SelectField('Month', choices=months, validators=[DataRequired()])
    # Address details
    address_name = StringField('Address Nickname', validators=[DataRequired()])
    address_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_2 = StringField('Address Line 2')
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('Zip Code', validators=[DataRequired()])
