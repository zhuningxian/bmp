from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    occupation = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    borrowings = db.relationship('Borrowing', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'occupation': self.occupation,
            'created_at': self.created_at.isoformat()
        }

class Book(db.Model):
    """图书模型"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100))
    publish_year = db.Column(db.Integer)
    category = db.Column(db.String(50))
    language = db.Column(db.String(20), default='中文')
    pages = db.Column(db.Integer)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(200))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    borrowings = db.relationship('Borrowing', backref='book', lazy=True)
    ratings = db.relationship('Rating', backref='book', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'publish_year': self.publish_year,
            'category': self.category,
            'language': self.language,
            'pages': self.pages,
            'description': self.description,
            'cover_url': self.cover_url,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'created_at': self.created_at.isoformat()
        }

class Borrowing(db.Model):
    """借阅记录模型"""
    __tablename__ = 'borrowings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')  # borrowed, returned, overdue
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status
        }

class Rating(db.Model):
    """评分模型"""
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1-5星评分
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat()
        }

class UserBehavior(db.Model):
    """用户行为模型"""
    __tablename__ = 'user_behaviors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    behavior_type = db.Column(db.String(20), nullable=False)  # view, search, bookmark, share
    duration = db.Column(db.Integer)  # 停留时间（秒）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'behavior_type': self.behavior_type,
            'duration': self.duration,
            'created_at': self.created_at.isoformat()
        }