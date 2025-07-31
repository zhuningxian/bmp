from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import numpy as np

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    occupation = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    borrowings = db.relationship('Borrowing', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class Book(db.Model):
    """图书模型"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    publish_year = db.Column(db.Integer)
    category = db.Column(db.String(50))
    language = db.Column(db.String(20))
    pages = db.Column(db.Integer)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    
    # 关系
    borrowings = db.relationship('Borrowing', backref='book', lazy=True)
    ratings = db.relationship('Rating', backref='book', lazy=True)
    
    def __repr__(self):
        return f'<Book {self.title}>'

class Borrowing(db.Model):
    """借阅记录模型"""
    __tablename__ = 'borrowings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='borrowed')  # borrowed, returned, overdue
    
    def __repr__(self):
        return f'<Borrowing {self.user_id}-{self.book_id}>'

class Rating(db.Model):
    """评分模型"""
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1-5星评分
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Rating {self.user_id}-{self.book_id}: {self.rating}>'

class UserBehavior(db.Model):
    """用户行为模型"""
    __tablename__ = 'user_behaviors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    behavior_type = db.Column(db.String(20), nullable=False)  # view, search, wishlist, borrow
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<UserBehavior {self.user_id}-{self.book_id}: {self.behavior_type}>'