from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    age = Column(Integer)
    occupation = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    borrowings = relationship("Borrowing", back_populates="user")
    ratings = relationship("Rating", back_populates="user")

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    isbn = Column(String(20), unique=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200))
    publisher = Column(String(100))
    publication_year = Column(Integer)
    category = Column(String(50))
    description = Column(Text)
    language = Column(String(20))
    pages = Column(Integer)
    
    # 关系
    borrowings = relationship("Borrowing", back_populates="book")
    ratings = relationship("Rating", back_populates="book")

class Borrowing(Base):
    __tablename__ = 'borrowings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    borrow_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime)
    due_date = Column(DateTime)
    
    # 关系
    user = relationship("User", back_populates="borrowings")
    book = relationship("Book", back_populates="borrowings")

class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    rating = Column(Float, nullable=False)  # 1-5 评分
    review = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="ratings")
    book = relationship("Book", back_populates="ratings")

# 数据库引擎和会话
engine = create_engine('sqlite:///library_recommendation.db', echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """创建所有数据表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()