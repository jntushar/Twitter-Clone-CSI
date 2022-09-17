from modules import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User_mgmt.query.get(int(user_id))


class User_mgmt(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    bg_file = db.Column(db.String(20), nullable=False, default='default_bg.jpg')
    bio = db.Column(db.String(200))
    date = db.Column(db.String(20))
    bday = db.Column(db.String(10))

    posts = db.relationship('Post', backref='author', lazy=True)
    following = db.relationship('Following', backref='follow', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweet = db.Column(db.String(500), nullable=False)
    stamp = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_mgmt.id'), nullable=False)


class Following(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, nullable=False)  # following
    user_id = db.Column(db.Integer, db.ForeignKey('user_mgmt.id'), nullable=False)  # follower
