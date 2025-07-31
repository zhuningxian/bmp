import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sqlalchemy.orm import Session
from models.database import User, Book, Rating, Borrowing

class CollaborativeFilteringRecommender:
    """协同过滤推荐系统"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_item_matrix = None
        self.svd_model = None
        self.books_df = None
        self.users_df = None
        
    def load_data(self):
        """从数据库加载数据"""
        # 加载评分数据
        ratings_query = self.db_session.query(Rating).all()
        ratings_data = []
        for rating in ratings_query:
            ratings_data.append({
                'user_id': rating.user_id,
                'book_id': rating.book_id,
                'rating': rating.rating
            })
        
        self.ratings_df = pd.DataFrame(ratings_data)
        
        # 加载图书数据
        books_query = self.db_session.query(Book).all()
        books_data = []
        for book in books_query:
            books_data.append({
                'book_id': book.id,
                'title': book.title,
                'author': book.author,
                'category': book.category,
                'description': book.description
            })
        
        self.books_df = pd.DataFrame(books_data)
        
        # 加载用户数据
        users_query = self.db_session.query(User).all()
        users_data = []
        for user in users_query:
            users_data.append({
                'user_id': user.id,
                'username': user.username,
                'age': user.age,
                'occupation': user.occupation
            })
        
        self.users_df = pd.DataFrame(users_data)
        
    def create_user_item_matrix(self):
        """创建用户-物品矩阵"""
        if self.ratings_df.empty:
            return None
            
        self.user_item_matrix = self.ratings_df.pivot_table(
            index='user_id', 
            columns='book_id', 
            values='rating',
            fill_value=0
        )
        return self.user_item_matrix
    
    def train_svd_model(self):
        """训练SVD模型"""
        if self.user_item_matrix is None or self.user_item_matrix.empty:
            return None
            
        # 使用Scikit-learn的TruncatedSVD替代surprise
        n_components = min(50, min(self.user_item_matrix.shape) - 1)
        if n_components <= 0:
            return None
            
        self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
        self.user_features = self.svd_model.fit_transform(self.user_item_matrix)
        self.item_features = self.svd_model.components_.T
        
        return self.svd_model
    
    def get_user_based_recommendations(self, user_id, n_recommendations=10):
        """基于用户的协同过滤推荐"""
        if self.user_item_matrix is None:
            self.create_user_item_matrix()
            
        if self.user_item_matrix is None or user_id not in self.user_item_matrix.index:
            return []
            
        # 计算用户相似度
        user_similarities = cosine_similarity(self.user_item_matrix)
        user_sim_df = pd.DataFrame(
            user_similarities,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        # 获取相似用户
        similar_users = user_sim_df[user_id].sort_values(ascending=False)[1:11]
        
        # 获取用户已评分的图书
        user_books = set(self.user_item_matrix.loc[user_id][
            self.user_item_matrix.loc[user_id] > 0
        ].index)
        
        # 推荐逻辑
        recommendations = {}
        for similar_user, similarity in similar_users.items():
            similar_user_books = self.user_item_matrix.loc[similar_user]
            for book_id, rating in similar_user_books.items():
                if rating > 0 and book_id not in user_books:
                    if book_id not in recommendations:
                        recommendations[book_id] = 0
                    recommendations[book_id] += similarity * rating
        
        # 排序并返回推荐
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [(book_id, score) for book_id, score in sorted_recommendations[:n_recommendations]]
    
    def get_svd_recommendations(self, user_id, n_recommendations=10):
        """使用SVD模型进行推荐"""
        if self.svd_model is None:
            self.train_svd_model()
            
        if self.svd_model is None or user_id not in self.user_item_matrix.index:
            return []
            
        # 获取用户已评分的图书
        user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
        rated_books = set(user_ratings['book_id'].values)
        
        # 获取所有图书
        all_books = set(self.ratings_df['book_id'].unique())
        unrated_books = all_books - rated_books
        
        # 预测评分
        user_idx = list(self.user_item_matrix.index).index(user_id)
        user_vector = self.user_features[user_idx]
        
        predictions = []
        for book_id in unrated_books:
            if book_id in self.user_item_matrix.columns:
                book_idx = list(self.user_item_matrix.columns).index(book_id)
                book_vector = self.item_features[book_idx]
                predicted_rating = np.dot(user_vector, book_vector)
                predictions.append((book_id, predicted_rating))
        
        # 排序并返回推荐
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n_recommendations]
    
    def get_item_based_recommendations(self, user_id, n_recommendations=10):
        """基于物品的协同过滤推荐"""
        if self.user_item_matrix is None:
            self.create_user_item_matrix()
            
        if self.user_item_matrix is None:
            return []
            
        # 转置矩阵以计算物品相似度
        item_user_matrix = self.user_item_matrix.T
        item_similarities = cosine_similarity(item_user_matrix)
        item_sim_df = pd.DataFrame(
            item_similarities,
            index=item_user_matrix.index,
            columns=item_user_matrix.index
        )
        
        # 获取用户评分的图书
        if user_id not in self.user_item_matrix.index:
            return []
            
        user_ratings = self.user_item_matrix.loc[user_id]
        user_books = user_ratings[user_ratings > 0]
        
        recommendations = {}
        
        # 对每本用户评分的图书，找相似图书
        for book_id, rating in user_books.items():
            similar_books = item_sim_df[book_id].sort_values(ascending=False)[1:11]
            
            for similar_book, similarity in similar_books.items():
                if similar_book not in user_books.index:
                    if similar_book not in recommendations:
                        recommendations[similar_book] = 0
                    recommendations[similar_book] += similarity * rating
        
        # 排序并返回推荐
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [(book_id, score) for book_id, score in sorted_recommendations[:n_recommendations]]