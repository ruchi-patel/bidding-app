from . import db


class User(db.Model):

    __tablename__ = 'users'
    email = db.Column(db.String(80), primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile_picture = db.Column(db.String(256), nullable=True, default="animated-cat-13.jpg")
