from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, InputRequired
from flask_wtf.file import FileField, FileRequired
from .choices import product_categories
from wtforms.fields import (StringField, SelectField, FloatField, DateField, TimeField, TextAreaField)

class ProductRegistrationForm(FlaskForm):
    name = StringField('Name of the Product', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=product_categories)
    base_price = FloatField('Base price')
    article_image = FileField('Product Image', validators=[FileRequired()])
    is_biddable = SelectField('Is Product up for Bid ?', choices=[('True','Yes'),('False','No')])
    bid_end_day = DateField('Select Bid End Date', format = '%d-%m-%Y')
    bid_end_time = TimeField('Select Bid End Date and Time', format = '%H:%M')

