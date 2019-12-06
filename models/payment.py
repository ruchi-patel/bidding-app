from . import db


class Payment(db.Model):

    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True)
    payment_user_id = db.Column(db.String(80), db.ForeignKey('users.email'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    year = db.Column(db.String(80), nullable=False)
    month = db.Column(db.String(80), nullable=False)
    name_on_card = db.Column(db.String(80), nullable=False)
    card_no = db.Column(db.Integer, nullable=False)
    payment_type = db.Column(db.String(80), nullable=False)
