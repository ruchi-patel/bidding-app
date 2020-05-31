from . import db
import datetime


class OrderConfirmation(db.Model):

    __tablename__ = 'Order_confirmation'
    order_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('Address_details.address_id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.payment_id'), nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey('users.email'), nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)

