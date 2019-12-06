from . import db
import datetime


class Order(db.Model):

    __tablename__ = 'Order'
    order_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('Address_details.address_id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.payment_id'), nullable=False)
    bid_id = db.Column(db.String(80), db.ForeignKey('bids.bid_id'), nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

