from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    questions = db.relationship('Question', backref='category', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    wagered_points = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.String(1000),nullable=True)
    answered_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_answered = db.Column(db.Boolean, default=False)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    points = db.Column(db.Integer, default=0)
    rank = db.Column(db.String(50), default="Beginner")  # User rank
    time_spent = db.Column(db.Integer, default=0)  # User rank
#video metadata
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    upload_date = db.Column(db.DateTime, nullable=False, default=func.now())
    content = db.Column(db.LargeBinary, nullable=False)  # Store the video as binary data

    def __repr__(self):
        return f'<Video {self.filename}>'

