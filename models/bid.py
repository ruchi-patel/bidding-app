from . import db


class Bid(db.Model):

    __tablename__ = 'bids'
    bid_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    bidder_id = db.Column(db.String(80), db.ForeignKey('users.email'), nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)
