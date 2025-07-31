from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
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
    # 获取最新图书
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(8).all()
    
    # 获取热门图书
    popular_books = Book.query.join(Borrowing).group_by(Book.id).order_by(
        db.func.count(Borrowing.id).desc()
    ).limit(8).all()
    
    return render_template('index.html', 
                         recent_books=recent_books, 
                         popular_books=popular_books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        occupation = request.form.get('occupation')
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='用户名已存在')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='邮箱已存在')
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            age=int(age) if age else None,
            gender=gender,
            occupation=occupation
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """用户仪表板"""
    # 获取用户借阅历史
    borrowings = Borrowing.query.filter_by(user_id=current_user.id).order_by(
        Borrowing.borrow_date.desc()
    ).limit(10).all()
    
    # 获取用户评分
    ratings = Rating.query.filter_by(user_id=current_user.id).order_by(
        Rating.created_at.desc()
    ).limit(10).all()
    
    return render_template('dashboard.html', 
                         borrowings=borrowings, 
                         ratings=ratings)

@app.route('/books')
def books():
    """图书列表页面"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Book.query
    
    if category:
        query = query.filter(Book.category == category)
    
    if search:
        query = query.filter(
            db.or_(
                Book.title.contains(search),
                Book.author.contains(search),
                Book.description.contains(search)
            )
        )
    
    books = query.paginate(page=page, per_page=20, error_out=False)
    categories = db.session.query(Book.category).distinct().all()
    
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
            duration=0
        )
        db.session.add(behavior)
        db.session.commit()
    
    # 获取相关图书推荐
    related_books = Book.query.filter(
        Book.category == book.category,
        Book.id != book_id
    ).limit(6).all()
    
    # 获取评分
    ratings = Rating.query.filter_by(book_id=book_id).order_by(
        Rating.created_at.desc()
    ).limit(10).all()
    
    return render_template('book_detail.html', 
                         book=book, 
                         related_books=related_books,
                         ratings=ratings)

@app.route('/api/recommendations')
@login_required
def get_recommendations():
    """获取个性化推荐"""
    try:
        recommendations = recommendation_engine.get_personalized_recommendations(
            current_user.id, 10
        )
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rate_book', methods=['POST'])
@login_required
def rate_book():
    """评分图书"""
    data = request.get_json()
    book_id = data.get('book_id')
    rating = data.get('rating')
    review = data.get('review', '')
    
    # 检查是否已经评分
    existing_rating = Rating.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id
    ).first()
    
    if existing_rating:
        existing_rating.rating = rating
        existing_rating.review = review
        existing_rating.created_at = datetime.now()
    else:
        new_rating = Rating(
            user_id=current_user.id,
            book_id=book_id,
            rating=rating,
            review=review
        )
        db.session.add(new_rating)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/borrow_book', methods=['POST'])
@login_required
def borrow_book():
    """借阅图书"""
    data = request.get_json()
    book_id = data.get('book_id')
    
    book = Book.query.get(book_id)
    if not book or book.available_copies <= 0:
        return jsonify({'success': False, 'error': '图书不可借'})
    
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
    
    return jsonify({'success': True})

@app.route('/api/return_book', methods=['POST'])
@login_required
def return_book():
    """归还图书"""
    data = request.get_json()
    borrowing_id = data.get('borrowing_id')
    
    borrowing = Borrowing.query.get(borrowing_id)
    if not borrowing or borrowing.user_id != current_user.id:
        return jsonify({'success': False, 'error': '借阅记录不存在'})
    
    # 更新借阅记录
    borrowing.return_date = datetime.now()
    borrowing.status = 'returned'
    
    # 更新图书可用数量
    book = borrowing.book
    book.available_copies += 1
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/search_books')
def search_books():
    """搜索图书API"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return jsonify({'success': False, 'error': '搜索关键词不能为空'})
    
    books = Book.query.filter(
        db.or_(
            Book.title.contains(query),
            Book.author.contains(query),
            Book.description.contains(query)
        )
    ).paginate(page=page, per_page=10, error_out=False)
    
    return jsonify({
        'success': True,
        'books': [book.to_dict() for book in books.items],
        'total': books.total,
        'pages': books.pages,
        'current_page': books.page
    })

@app.route('/api/user_behavior', methods=['POST'])
@login_required
def record_behavior():
    """记录用户行为"""
    data = request.get_json()
    book_id = data.get('book_id')
    behavior_type = data.get('behavior_type')
    duration = data.get('duration', 0)
    
    behavior = UserBehavior(
        user_id=current_user.id,
        book_id=book_id,
        behavior_type=behavior_type,
        duration=duration
    )
    
    db.session.add(behavior)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/generate_data')
def generate_data():
    """生成模拟数据（管理员功能）"""
    try:
        generator = DataGenerator()
        generator.generate_all_data()
        return jsonify({'success': True, 'message': '数据生成成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/stats')
def admin_stats():
    """管理员统计页面"""
    total_users = User.query.count()
    total_books = Book.query.count()
    total_borrowings = Borrowing.query.count()
    total_ratings = Rating.query.count()
    
    # 按类别统计图书
    category_stats = db.session.query(
        Book.category, 
        db.func.count(Book.id)
    ).group_by(Book.category).all()
    
    # 最近借阅趋势
    recent_borrowings = db.session.query(
        db.func.date(Borrowing.borrow_date),
        db.func.count(Borrowing.id)
    ).filter(
        Borrowing.borrow_date >= datetime.now() - timedelta(days=30)
    ).group_by(
        db.func.date(Borrowing.borrow_date)
    ).all()
    
    return render_template('admin_stats.html',
                         total_users=total_users,
                         total_books=total_books,
                         total_borrowings=total_borrowings,
                         total_ratings=total_ratings,
                         category_stats=category_stats,
                         recent_borrowings=recent_borrowings)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)