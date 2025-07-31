from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import pandas as pd
from datetime import datetime
import os

from recommendation_engine import RecommendationEngine
from data_models import LibraryDatabase
from user_behavior_analyzer import UserBehaviorAnalyzer

app = Flask(__name__)
CORS(app)

# 初始化组件
db = LibraryDatabase()
behavior_analyzer = UserBehaviorAnalyzer(db)
recommendation_engine = RecommendationEngine(db)

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取所有用户列表"""
    users = db.get_all_users()
    return jsonify({'users': users})

@app.route('/api/books', methods=['GET'])
def get_books():
    """获取所有图书列表"""
    books = db.get_all_books()
    return jsonify({'books': books})

@app.route('/api/user/<int:user_id>/recommendations', methods=['GET'])
def get_user_recommendations(user_id):
    """获取用户推荐"""
    method = request.args.get('method', 'hybrid')
    num_recommendations = int(request.args.get('num', 10))
    
    try:
        recommendations = recommendation_engine.get_recommendations(
            user_id, method=method, num_recommendations=num_recommendations
        )
        return jsonify({
            'user_id': user_id,
            'method': method,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/user/<int:user_id>/behavior', methods=['GET'])
def get_user_behavior(user_id):
    """获取用户行为分析"""
    behavior = behavior_analyzer.analyze_user_behavior(user_id)
    return jsonify({
        'user_id': user_id,
        'behavior_analysis': behavior
    })

@app.route('/api/user/<int:user_id>/rate_book', methods=['POST'])
def rate_book(user_id):
    """用户评分图书"""
    data = request.get_json()
    book_id = data.get('book_id')
    rating = data.get('rating')
    
    if not all([book_id, rating]):
        return jsonify({'error': '缺少必要参数'}), 400
    
    try:
        db.add_rating(user_id, book_id, rating)
        return jsonify({'message': '评分成功添加'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/user/<int:user_id>/borrow_book', methods=['POST'])
def borrow_book(user_id):
    """用户借阅图书"""
    data = request.get_json()
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({'error': '缺少图书ID'}), 400
    
    try:
        db.add_borrowing(user_id, book_id)
        return jsonify({'message': '借阅记录成功添加'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """获取系统统计信息"""
    stats = {
        'total_users': len(db.get_all_users()),
        'total_books': len(db.get_all_books()),
        'total_ratings': len(db.ratings_df),
        'total_borrowings': len(db.borrowings_df)
    }
    return jsonify(stats)

if __name__ == '__main__':
    # 初始化数据
    if not os.path.exists('data'):
        os.makedirs('data')
        db.generate_demo_data()
        recommendation_engine.train_models()
    
    app.run(debug=True, host='0.0.0.0', port=5000)