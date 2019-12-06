from flask_wtf import FlaskForm, RecaptchaField
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.fields.html5 import EmailField


class SignupForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired(message="Please enter a password.")])
    confirm_password = PasswordField('Confirm Password', [EqualTo('password', message='Passwords must match.')])