from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from models.database import engine, User, Book, Rating, Borrowing
from algorithms.hybrid_recommender import HybridRecommender
import json

# 创建蓝图
recommendation_bp = Blueprint('recommendation', __name__)

# 数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_book_info(book_id, db_session):
    """获取图书基本信息"""
    book = db_session.query(Book).filter(Book.id == book_id).first()
    if book:
        return {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'category': book.category,
            'description': book.description,
            'publication_year': book.publication_year,
            'language': book.language,
            'pages': book.pages
        }
    return None

@recommendation_bp.route('/recommendations/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """获取用户推荐"""
    try:
        db_session = SessionLocal()
        
        # 获取参数
        n_recommendations = int(request.args.get('limit', 10))
        recommendation_type = request.args.get('type', 'adaptive')
        
        # 初始化推荐系统
        recommender = HybridRecommender(db_session)
        recommender.initialize()
        
        # 根据类型获取推荐
        if recommendation_type == 'adaptive':
            recommendations = recommender.get_adaptive_recommendations(
                user_id, n_recommendations
            )
        elif recommendation_type == 'hybrid':
            recommendations = recommender.get_hybrid_recommendations(
                user_id, n_recommendations
            )
        elif recommendation_type == 'collaborative':
            recommendations = recommender.cf_recommender.get_svd_recommendations(
                user_id, n_recommendations
            )
        elif recommendation_type == 'content':
            recommendations = recommender.cb_recommender.get_content_based_recommendations(
                user_id, n_recommendations
            )
        else:
            recommendations = recommender.get_adaptive_recommendations(
                user_id, n_recommendations
            )
        
        # 获取图书详细信息
        detailed_recommendations = []
        for book_id, score in recommendations:
            book_info = get_book_info(book_id, db_session)
            if book_info:
                book_info['recommendation_score'] = round(score, 3)
                detailed_recommendations.append(book_info)
        
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'recommendation_type': recommendation_type,
            'recommendations': detailed_recommendations
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recommendation_bp.route('/recommendations/<int:user_id>/category/<category>', methods=['GET'])
def get_category_recommendations(user_id, category):
    """按类别获取推荐"""
    try:
        db_session = SessionLocal()
        n_recommendations = int(request.args.get('limit', 10))
        
        recommender = HybridRecommender(db_session)
        recommender.initialize()
        
        recommendations = recommender.get_category_recommendations(
            user_id, category, n_recommendations
        )
        
        # 获取图书详细信息
        detailed_recommendations = []
        for book_id, score in recommendations:
            book_info = get_book_info(book_id, db_session)
            if book_info:
                book_info['recommendation_score'] = round(score, 3)
                detailed_recommendations.append(book_info)
        
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'category': category,
            'recommendations': detailed_recommendations
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recommendation_bp.route('/books/<int:book_id>/recommendations', methods=['GET'])
def get_similar_books(book_id):
    """获取相似图书推荐"""
    try:
        db_session = SessionLocal()
        n_recommendations = int(request.args.get('limit', 10))
        
        recommender = HybridRecommender(db_session)
        recommender.initialize()
        
        book_details = recommender.get_book_details_with_recommendations(book_id)
        
        if not book_details:
            return jsonify({
                'status': 'error',
                'message': '图书不存在'
            }), 404
        
        # 获取相似图书详细信息
        similar_books = []
        for similar_book_id, similarity in book_details['similar_books'][:n_recommendations]:
            book_info = get_book_info(similar_book_id, db_session)
            if book_info:
                book_info['similarity_score'] = round(similarity, 3)
                similar_books.append(book_info)
        
        # 计算平均评分
        ratings = book_details['average_rating']
        avg_rating = sum([r[0] for r in ratings]) / len(ratings) if ratings else 0
        
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'book': get_book_info(book_id, SessionLocal()),
            'borrowing_count': book_details['borrowing_count'],
            'average_rating': round(avg_rating, 1),
            'similar_books': similar_books
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recommendation_bp.route('/search', methods=['GET'])
def search_books():
    """搜索图书"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': '搜索关键词不能为空'
            }), 400
        
        db_session = SessionLocal()
        
        recommender = HybridRecommender(db_session)
        recommender.initialize()
        
        search_results = recommender.cb_recommender.search_books(query, limit)
        
        # 获取图书详细信息
        detailed_results = []
        for book_id, score in search_results:
            book_info = get_book_info(book_id, db_session)
            if book_info:
                book_info['relevance_score'] = round(score, 3)
                detailed_results.append(book_info)
        
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': detailed_results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recommendation_bp.route('/users/<int:user_id>/rating', methods=['POST'])
def add_rating(user_id):
    """添加图书评分"""
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        rating = data.get('rating')
        review = data.get('review', '')
        
        if not all([user_id, book_id, rating]):
            return jsonify({
                'status': 'error',
                'message': '用户ID、图书ID和评分不能为空'
            }), 400
        
        if not (1 <= rating <= 5):
            return jsonify({
                'status': 'error',
                'message': '评分必须在1-5之间'
            }), 400
        
        db_session = SessionLocal()
        
        # 检查是否已经评分
        existing_rating = db_session.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.book_id == book_id
        ).first()
        
        if existing_rating:
            # 更新评分
            existing_rating.rating = rating
            existing_rating.review = review
        else:
            # 添加新评分
            new_rating = Rating(
                user_id=user_id,
                book_id=book_id,
                rating=rating,
                review=review
            )
            db_session.add(new_rating)
        
        db_session.commit()
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'message': '评分添加成功'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recommendation_bp.route('/users/<int:user_id>/similar', methods=['GET'])
def get_similar_users(user_id):
    """获取相似用户"""
    try:
        db_session = SessionLocal()
        limit = int(request.args.get('limit', 10))
        
        recommender = HybridRecommender(db_session)
        recommender.initialize()
        
        similar_users = recommender.get_similar_users(user_id, limit)
        
        # 获取用户详细信息
        detailed_users = []
        for similar_user_id, similarity in similar_users:
            user = db_session.query(User).filter(User.id == similar_user_id).first()
            if user:
                detailed_users.append({
                    'id': user.id,
                    'username': user.username,
                    'similarity_score': round(similarity, 3)
                })
        
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'similar_users': detailed_users
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recommendation_bp.route('/recommendations/<int:user_id>/<int:book_id>/explain', methods=['GET'])
def explain_recommendation(user_id, book_id):
    """解释推荐原因"""
    try:
        db_session = SessionLocal()
        
        recommender = HybridRecommender(db_session)
        recommender.initialize()
        
        explanations = recommender.explain_recommendation(user_id, book_id)
        
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'book_id': book_id,
            'explanations': explanations
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recommendation_bp.route('/popular', methods=['GET'])
def get_popular_books():
    """获取热门图书"""
    try:
        db_session = SessionLocal()
        limit = int(request.args.get('limit', 10))
        
        recommender = HybridRecommender(db_session)
        recommender.initialize()
        
        popular_books = recommender.cb_recommender.get_popular_books(limit)
        
        # 获取图书详细信息
        detailed_books = []
        for book_id, popularity_score in popular_books:
            book_info = get_book_info(book_id, db_session)
            if book_info:
                book_info['popularity_score'] = popularity_score
                detailed_books.append(book_info)
        
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'popular_books': detailed_books
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recommendation_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有图书类别"""
    try:
        db_session = SessionLocal()
        
        categories = db_session.query(Book.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        db_session.close()
        
        return jsonify({
            'status': 'success',
            'categories': category_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500