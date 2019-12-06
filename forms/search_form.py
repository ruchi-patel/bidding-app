from flask_wtf import FlaskForm
from wtforms.fields import StringField, SelectField
from wtforms.validators import DataRequired, InputRequired
from .choices import product_categories

class SearchForm(FlaskForm):
    category = SelectField('Category', choices=product_categories, validators=[InputRequired()])
    product_name = StringField('Product Name')

    def validate(self):
        article_name = self.article_name.data
        category = self.category.data

        if not category and not article_name:
            return False
        else:
            return True