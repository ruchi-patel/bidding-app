from . import db


class Address(db.Model):

    __tablename__ = 'Address_details'
    address_id = db.Column(db.Integer, primary_key=True)
    address_1 = db.Column(db.String(80), nullable=False)
    address_2 = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    zip_code = db.Column(db.Integer, default=0)
    address_name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey('users.email'), nullable=False)
