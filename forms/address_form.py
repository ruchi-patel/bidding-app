from flask_wtf import FlaskForm
from wtforms.fields import (StringField)
from wtforms.validators import DataRequired


class AddressForm(FlaskForm):
    name = StringField('Address Nickname', validators=[DataRequired()])
    address_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_2 = StringField('Address Line 2')
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('Zip Code', validators=[DataRequired()])


