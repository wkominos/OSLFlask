from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class LibraryUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    preferred_name = db.Column(db.String(64))
    email_address = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(64))
    first_address = db.Column(db.String(255))
    second_address = db.Column(db.String(255))
    agency_code = db.Column(db.String(64)) #, db.ForeignKey('agency.code'))
    date_created = db.Column(db.String(255)) #might need this to be a string
    date_of_birth = db.Column(db.String(255))
    extended_info = db.Column(db.Text) #testing if text field works like this 

    def __repr__(self):
        return '<LibraryUser {} {}: {}>'.format(self.first_name, self.last_name, self.user_id)