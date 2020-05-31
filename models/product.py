import datetime

from . import db


class Product(db.Model):

    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    product_image = db.Column(db.String(256), nullable=False, default="123.jpg")
    end_day = db.Column(db.Date, default=datetime.datetime.now())
    end_time = db.Column(db.Time, default=datetime.time())
    views = db.Column(db.Integer, default=0)
    is_biddable = db.Column(db.Boolean, default=False)
    seller_id = db.Column(db.String(80), db.ForeignKey('users.email'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
