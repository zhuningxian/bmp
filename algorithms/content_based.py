import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from models.database import User, Book, Rating, Borrowing
import re

class ContentBasedRecommender:
    """基于内容的推荐系统"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.books_df = None
        self.content_matrix = None
        self.tfidf_vectorizer = None
        self.book_similarity = None
        
    def load_data(self):
        """从数据库加载图书数据"""
        books_query = self.db_session.query(Book).all()
        books_data = []
        
        for book in books_query:
            # 合并图书的文本特征
            content_features = []
            if book.title:
                content_features.append(book.title)
            if book.author:
                content_features.append(book.author)
            if book.category:
                content_features.append(book.category)
            if book.description:
                content_features.append(book.description)
            
            combined_features = ' '.join(content_features)
            
            books_data.append({
                'book_id': book.id,
                'title': book.title,
                'author': book.author,
                'category': book.category,
                'description': book.description,
                'publication_year': book.publication_year,
                'language': book.language,
                'combined_features': combined_features
            })
        
        self.books_df = pd.DataFrame(books_data)
        
    def preprocess_text(self, text):
        """文本预处理"""
        if pd.isna(text) or text == '':
            return ''
        
        # 转小写
        text = text.lower()
        # 移除特殊字符，保留中英文和数字
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def create_content_matrix(self):
        """创建内容特征矩阵"""
        if self.books_df is None or self.books_df.empty:
            return None
        
        # 预处理文本
        self.books_df['processed_features'] = self.books_df['combined_features'].apply(
            self.preprocess_text
        )
        
        # 使用TF-IDF向量化
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8
        )
        
        # 创建TF-IDF矩阵
        self.content_matrix = self.tfidf_vectorizer.fit_transform(
            self.books_df['processed_features']
        )
        
        return self.content_matrix
    
    def calculate_book_similarity(self):
        """计算图书之间的相似度"""
        if self.content_matrix is None:
            self.create_content_matrix()
            
        if self.content_matrix is None:
            return None
            
        # 计算余弦相似度
        self.book_similarity = cosine_similarity(self.content_matrix)
        
        return self.book_similarity
    
    def get_content_based_recommendations(self, user_id, n_recommendations=10):
        """基于内容的推荐"""
        if self.book_similarity is None:
            self.calculate_book_similarity()
            
        if self.book_similarity is None:
            return []
        
        # 获取用户的评分历史
        user_ratings = self.db_session.query(Rating).filter(
            Rating.user_id == user_id
        ).all()
        
        if not user_ratings:
            # 如果用户没有评分历史，使用借阅历史
            user_borrowings = self.db_session.query(Borrowing).filter(
                Borrowing.user_id == user_id
            ).all()
            
            if not user_borrowings:
                return self.get_popular_books(n_recommendations)
            
            # 基于借阅历史推荐
            return self.recommend_based_on_borrowings(user_borrowings, n_recommendations)
        
        # 基于评分历史推荐
        return self.recommend_based_on_ratings(user_ratings, n_recommendations)
    
    def recommend_based_on_ratings(self, user_ratings, n_recommendations):
        """基于用户评分历史推荐"""
        recommendations = {}
        rated_books = set()
        
        for rating in user_ratings:
            book_id = rating.book_id
            user_rating = rating.rating
            rated_books.add(book_id)
            
            # 找到该图书在DataFrame中的索引
            book_idx = self.books_df[self.books_df['book_id'] == book_id].index
            if len(book_idx) == 0:
                continue
                
            book_idx = book_idx[0]
            
            # 获取相似图书
            similar_books = list(enumerate(self.book_similarity[book_idx]))
            similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)
            
            # 根据用户评分加权推荐
            weight = user_rating / 5.0  # 归一化评分
            
            for idx, similarity in similar_books[1:51]:  # 取前50个相似图书
                similar_book_id = self.books_df.iloc[idx]['book_id']
                
                if similar_book_id not in rated_books:
                    if similar_book_id not in recommendations:
                        recommendations[similar_book_id] = 0
                    recommendations[similar_book_id] += similarity * weight
        
        # 排序并返回推荐
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [(book_id, score) for book_id, score in sorted_recommendations[:n_recommendations]]
    
    def recommend_based_on_borrowings(self, user_borrowings, n_recommendations):
        """基于借阅历史推荐"""
        recommendations = {}
        borrowed_books = set()
        
        for borrowing in user_borrowings:
            book_id = borrowing.book_id
            borrowed_books.add(book_id)
            
            # 找到该图书在DataFrame中的索引
            book_idx = self.books_df[self.books_df['book_id'] == book_id].index
            if len(book_idx) == 0:
                continue
                
            book_idx = book_idx[0]
            
            # 获取相似图书
            similar_books = list(enumerate(self.book_similarity[book_idx]))
            similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)
            
            for idx, similarity in similar_books[1:31]:  # 取前30个相似图书
                similar_book_id = self.books_df.iloc[idx]['book_id']
                
                if similar_book_id not in borrowed_books:
                    if similar_book_id not in recommendations:
                        recommendations[similar_book_id] = 0
                    recommendations[similar_book_id] += similarity
        
        # 排序并返回推荐
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [(book_id, score) for book_id, score in sorted_recommendations[:n_recommendations]]
    
    def get_popular_books(self, n_recommendations=10):
        """获取热门图书（新用户推荐）"""
        # 统计借阅次数
        borrowing_counts = self.db_session.query(
            Borrowing.book_id,
            Borrowing.book_id.label('count')
        ).group_by(Borrowing.book_id).all()
        
        if not borrowing_counts:
            # 如果没有借阅记录，返回最新的图书
            recent_books = self.db_session.query(Book).order_by(
                Book.publication_year.desc()
            ).limit(n_recommendations).all()
            
            return [(book.id, 1.0) for book in recent_books]
        
        # 按借阅次数排序
        popular_books = sorted(borrowing_counts, key=lambda x: x[1], reverse=True)
        
        return [(book_id, count) for book_id, count in popular_books[:n_recommendations]]
    
    def get_books_by_category(self, category, n_recommendations=10):
        """按类别推荐图书"""
        category_books = self.books_df[
            self.books_df['category'].str.contains(category, case=False, na=False)
        ]
        
        if category_books.empty:
            return []
            
        # 按出版年份排序，优先推荐新书
        category_books = category_books.sort_values(
            'publication_year', 
            ascending=False
        )
        
        return [(book_id, 1.0) for book_id in category_books['book_id'].head(n_recommendations)]
    
    def search_books(self, query, n_results=10):
        """图书搜索功能"""
        if self.books_df is None or self.books_df.empty:
            return []
            
        query = self.preprocess_text(query)
        
        # 在标题、作者、描述中搜索
        results = []
        
        for idx, row in self.books_df.iterrows():
            score = 0
            
            # 标题匹配
            if query in self.preprocess_text(str(row['title'])):
                score += 3
                
            # 作者匹配
            if query in self.preprocess_text(str(row['author'])):
                score += 2
                
            # 类别匹配
            if query in self.preprocess_text(str(row['category'])):
                score += 1.5
                
            # 描述匹配
            if query in self.preprocess_text(str(row['description'])):
                score += 1
            
            if score > 0:
                results.append((row['book_id'], score))
        
        # 排序并返回结果
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:n_results]