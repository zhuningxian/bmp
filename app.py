from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta

from models import db, User, Book, Borrowing, Rating, UserBehavior
from recommendation_engine import RecommendationEngine
from data_generator import DataGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 初始化推荐引擎
recommendation_engine = RecommendationEngine()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """首页"""
    # 获取热门图书
    popular_books = recommendation_engine.get_popular_books(8)
    popular_books_data = []
    for book_id in popular_books:
        book = Book.query.get(book_id)
        if book:
            popular_books_data.append(book)
    
    # 获取最新图书
    recent_books = recommendation_engine.get_recent_books(8)
    recent_books_data = []
    for book_id in recent_books:
        book = Book.query.get(book_id)
        if book:
            recent_books_data.append(book)
    
    return render_template('index.html', 
                         popular_books=popular_books_data,
                         recent_books=recent_books_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已存在')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """用户仪表板"""
    # 获取用户借阅历史
    borrowings = Borrowing.query.filter_by(user_id=current_user.id).order_by(
        Borrowing.borrow_date.desc()
    ).limit(10).all()
    
    # 获取个性化推荐
    recommended_books = recommendation_engine.get_personalized_recommendations(
        current_user.id, 8
    )
    recommended_books_data = []
    for book_id in recommended_books:
        book = Book.query.get(book_id)
        if book:
            recommended_books_data.append(book)
    
    return render_template('dashboard.html',
                         borrowings=borrowings,
                         recommended_books=recommended_books_data)

@app.route('/books')
def books():
    """图书列表页面"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Book.query
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            (Book.title.contains(search)) |
            (Book.author.contains(search)) |
            (Book.description.contains(search))
        )
    
    books = query.paginate(page=page, per_page=20, error_out=False)
    categories = db.session.query(Book.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('books.html', 
                         books=books,
                         categories=categories,
                         current_category=category,
                         search=search)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """图书详情页面"""
    book = Book.query.get_or_404(book_id)
    
    # 记录用户行为
    if current_user.is_authenticated:
        behavior = UserBehavior(
            user_id=current_user.id,
            book_id=book_id,
            behavior_type='view',
            session_id=request.session.get('session_id', 'default')
        )
        db.session.add(behavior)
        db.session.commit()
    
    # 获取相似图书
    similar_books = recommendation_engine.content_based_recommendations(
        current_user.id if current_user.is_authenticated else None, 6
    )
    similar_books_data = []
    for similar_book_id in similar_books:
        similar_book = Book.query.get(similar_book_id)
        if similar_book and similar_book.id != book_id:
            similar_books_data.append(similar_book)
    
    return render_template('book_detail.html', 
                         book=book,
                         similar_books=similar_books_data)

@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    """借阅图书"""
    book = Book.query.get_or_404(book_id)
    
    if book.available_copies > 0:
        # 创建借阅记录
        borrowing = Borrowing(
            user_id=current_user.id,
            book_id=book_id,
            due_date=datetime.now() + timedelta(days=30)
        )
        
        # 更新图书可用数量
        book.available_copies -= 1
        
        db.session.add(borrowing)
        db.session.commit()
        
        flash('借阅成功！')
    else:
        flash('图书已无可用副本')
    
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/return/<int:borrowing_id>', methods=['POST'])
@login_required
def return_book(borrowing_id):
    """归还图书"""
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    
    if borrowing.user_id != current_user.id:
        flash('您无权归还此图书')
        return redirect(url_for('dashboard'))
    
    borrowing.return_date = datetime.now()
    borrowing.status = 'returned'
    borrowing.book.available_copies += 1
    
    db.session.commit()
    flash('归还成功！')
    
    return redirect(url_for('dashboard'))

@app.route('/rate/<int:book_id>', methods=['POST'])
@login_required
def rate_book(book_id):
    """评分图书"""
    rating_value = float(request.form['rating'])
    review = request.form.get('review', '')
    
    # 检查是否已经评分
    existing_rating = Rating.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()
    
    if existing_rating:
        existing_rating.rating = rating_value
        existing_rating.review = review
    else:
        rating = Rating(
            user_id=current_user.id,
            book_id=book_id,
            rating=rating_value,
            review=review
        )
        db.session.add(rating)
    
    db.session.commit()
    flash('评分成功！')
    
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/api/recommendations')
@login_required
def api_recommendations():
    """推荐API"""
    algorithm = request.args.get('algorithm', 'hybrid')
    n_recommendations = int(request.args.get('n', 10))
    
    if algorithm == 'collaborative':
        recommendations = recommendation_engine.collaborative_filtering_recommendations(
            current_user.id, n_recommendations
        )
    elif algorithm == 'content':
        recommendations = recommendation_engine.content_based_recommendations(
            current_user.id, n_recommendations
        )
    elif algorithm == 'matrix':
        recommendations = recommendation_engine.matrix_factorization_recommendations(
            current_user.id, n_recommendations
        )
    else:
        recommendations = recommendation_engine.hybrid_recommendations(
            current_user.id, n_recommendations
        )
    
    books_data = []
    for book_id in recommendations:
        book = Book.query.get(book_id)
        if book:
            books_data.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'category': book.category,
                'cover_url': book.cover_url
            })
    
    return jsonify(books_data)

@app.route('/admin/generate-data')
def generate_data():
    """生成模拟数据（管理员功能）"""
    generator = DataGenerator()
    generator.generate_all_data()
    flash('模拟数据生成成功！')
    return redirect(url_for('index'))

@app.route('/admin/stats')
def admin_stats():
    """管理员统计页面"""
    total_users = User.query.count()
    total_books = Book.query.count()
    total_borrowings = Borrowing.query.count()
    total_ratings = Rating.query.count()
    
    # 借阅统计
    borrowings_by_month = db.session.query(
        db.func.strftime('%Y-%m', Borrowing.borrow_date).label('month'),
        db.func.count(Borrowing.id).label('count')
    ).group_by('month').order_by('month').all()
    
    # 热门分类
    popular_categories = db.session.query(
        Book.category,
        db.func.count(Borrowing.id).label('borrow_count')
    ).join(Borrowing).group_by(Book.category).order_by(
        db.func.count(Borrowing.id).desc()
    ).limit(10).all()
    
    return render_template('admin_stats.html',
                         total_users=total_users,
                         total_books=total_books,
                         total_borrowings=total_borrowings,
                         total_ratings=total_ratings,
                         borrowings_by_month=borrowings_by_month,
                         popular_categories=popular_categories)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)