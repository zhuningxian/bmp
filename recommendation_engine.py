import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
import warnings
warnings.filterwarnings('ignore')

class RecommendationEngine:
    """推荐引擎类"""
    
    def __init__(self, database):
        self.db = database
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.content_similarity_matrix = None
        self.svd_model = None
        self.user_item_matrix = None
        
    def train_models(self):
        """训练推荐模型"""
        print("开始训练推荐模型...")
        
        # 构建用户-物品评分矩阵
        self._build_user_item_matrix()
        
        # 训练协同过滤模型
        self._train_collaborative_filtering()
        
        # 训练内容过滤模型
        self._train_content_filtering()
        
        print("推荐模型训练完成！")
    
    def _build_user_item_matrix(self):
        """构建用户-物品评分矩阵"""
        if self.db.ratings_df.empty:
            print("警告: 没有评分数据")
            return
        
        # 创建用户-物品评分矩阵
        self.user_item_matrix = self.db.ratings_df.pivot_table(
            index='user_id', 
            columns='book_id', 
            values='rating', 
            fill_value=0
        )
        print(f"用户-物品矩阵形状: {self.user_item_matrix.shape}")
    
    def _train_collaborative_filtering(self):
        """训练协同过滤模型"""
        if self.user_item_matrix is None or self.user_item_matrix.empty:
            return
        
        # 用户相似度矩阵（基于用户）
        user_ratings = self.user_item_matrix.values
        self.user_similarity_matrix = cosine_similarity(user_ratings)
        
        # 物品相似度矩阵（基于物品）
        item_ratings = self.user_item_matrix.T.values
        self.item_similarity_matrix = cosine_similarity(item_ratings)
        
        # SVD矩阵分解降维
        try:
            self.svd_model = TruncatedSVD(n_components=min(50, self.user_item_matrix.shape[1]-1), random_state=42)
            self.user_features = self.svd_model.fit_transform(user_ratings)
            self.item_features = self.svd_model.components_.T
        except Exception as e:
            print(f"SVD训练失败: {e}")
            self.svd_model = None
        
        print("协同过滤模型训练完成")
    
    def _train_content_filtering(self):
        """训练内容过滤模型"""
        if self.db.books_df.empty:
            return
        
        # 构建图书内容特征
        books_df = self.db.books_df.copy()
        
        # 合并文本特征
        books_df['content_features'] = (
            books_df['category'].fillna('') + ' ' +
            books_df['author'].fillna('') + ' ' +
            books_df['description'].fillna('')
        )
        
        # TF-IDF向量化
        try:
            tfidf = TfidfVectorizer(max_features=1000, stop_words=None)
            content_matrix = tfidf.fit_transform(books_df['content_features'])
            
            # 计算内容相似度矩阵
            self.content_similarity_matrix = cosine_similarity(content_matrix)
            print("内容过滤模型训练完成")
        except Exception as e:
            print(f"内容过滤训练失败: {e}")
            self.content_similarity_matrix = None
    
    def get_recommendations(self, user_id, method='hybrid', num_recommendations=10):
        """获取推荐结果"""
        if method == 'collaborative':
            return self._collaborative_recommendations(user_id, num_recommendations)
        elif method == 'content':
            return self._content_recommendations(user_id, num_recommendations)
        elif method == 'popularity':
            return self._popularity_recommendations(num_recommendations)
        else:  # hybrid
            return self._hybrid_recommendations(user_id, num_recommendations)
    
    def _collaborative_recommendations(self, user_id, num_recommendations):
        """协同过滤推荐"""
        if self.user_item_matrix is None or user_id not in self.user_item_matrix.index:
            return self._popularity_recommendations(num_recommendations)
        
        try:
            # 基于用户的协同过滤
            user_idx = list(self.user_item_matrix.index).index(user_id)
            user_ratings = self.user_item_matrix.iloc[user_idx]
            
            # 找到相似用户
            user_similarities = self.user_similarity_matrix[user_idx]
            similar_users = np.argsort(user_similarities)[::-1][1:11]  # 取前10个相似用户
            
            # 计算推荐分数
            recommendations = {}
            for book_id in self.user_item_matrix.columns:
                if user_ratings[book_id] == 0:  # 用户未评分的书
                    score = 0
                    total_similarity = 0
                    
                    for similar_user_idx in similar_users:
                        similar_user_id = self.user_item_matrix.index[similar_user_idx]
                        similarity = user_similarities[similar_user_idx]
                        rating = self.user_item_matrix.iloc[similar_user_idx][book_id]
                        
                        if rating > 0:
                            score += similarity * rating
                            total_similarity += abs(similarity)
                    
                    if total_similarity > 0:
                        recommendations[book_id] = score / total_similarity
            
            # 排序并返回推荐
            sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
            return self._format_recommendations(sorted_recommendations[:num_recommendations], 'collaborative')
            
        except Exception as e:
            print(f"协同过滤推荐失败: {e}")
            return self._popularity_recommendations(num_recommendations)
    
    def _content_recommendations(self, user_id, num_recommendations):
        """内容过滤推荐"""
        if self.content_similarity_matrix is None:
            return self._popularity_recommendations(num_recommendations)
        
        try:
            # 获取用户历史评分高的书籍
            user_ratings = self.db.get_user_ratings(user_id)
            if user_ratings.empty:
                return self._popularity_recommendations(num_recommendations)
            
            # 找到用户喜欢的书籍（评分>=4）
            liked_books = user_ratings[user_ratings['rating'] >= 4]['book_id'].tolist()
            
            if not liked_books:
                return self._popularity_recommendations(num_recommendations)
            
            # 计算推荐分数
            recommendations = {}
            all_books = self.db.books_df['book_id'].tolist()
            
            for book_id in all_books:
                if book_id not in user_ratings['book_id'].tolist():  # 用户未评分的书
                    score = 0
                    count = 0
                    
                    # 获取图书在内容相似度矩阵中的索引
                    try:
                        book_idx = list(self.db.books_df['book_id']).index(book_id)
                        
                        for liked_book in liked_books:
                            liked_book_idx = list(self.db.books_df['book_id']).index(liked_book)
                            similarity = self.content_similarity_matrix[book_idx][liked_book_idx]
                            score += similarity
                            count += 1
                        
                        if count > 0:
                            recommendations[book_id] = score / count
                    except (ValueError, IndexError):
                        continue
            
            # 排序并返回推荐
            sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
            return self._format_recommendations(sorted_recommendations[:num_recommendations], 'content')
            
        except Exception as e:
            print(f"内容过滤推荐失败: {e}")
            return self._popularity_recommendations(num_recommendations)
    
    def _popularity_recommendations(self, num_recommendations):
        """基于流行度的推荐"""
        try:
            # 计算图书的平均评分和评分数量
            book_stats = self.db.ratings_df.groupby('book_id').agg({
                'rating': ['mean', 'count']
            }).round(2)
            book_stats.columns = ['avg_rating', 'rating_count']
            
            # 过滤掉评分数量过少的书籍
            popular_books = book_stats[book_stats['rating_count'] >= 3]
            
            # 计算流行度分数（结合平均评分和评分数量）
            popular_books['popularity_score'] = (
                popular_books['avg_rating'] * 0.7 + 
                np.log1p(popular_books['rating_count']) * 0.3
            )
            
            # 排序并取前N本
            top_books = popular_books.sort_values('popularity_score', ascending=False).head(num_recommendations)
            
            recommendations = [(book_id, score) for book_id, score in 
                             zip(top_books.index, top_books['popularity_score'])]
            
            return self._format_recommendations(recommendations, 'popularity')
            
        except Exception as e:
            print(f"流行度推荐失败: {e}")
            return []
    
    def _hybrid_recommendations(self, user_id, num_recommendations):
        """混合推荐算法"""
        try:
            # 获取各种推荐方法的结果
            collab_recs = self._collaborative_recommendations(user_id, num_recommendations * 2)
            content_recs = self._content_recommendations(user_id, num_recommendations * 2)
            popularity_recs = self._popularity_recommendations(num_recommendations)
            
            # 合并推荐结果
            hybrid_scores = {}
            
            # 协同过滤权重 0.4
            for rec in collab_recs:
                book_id = rec['book_id']
                hybrid_scores[book_id] = hybrid_scores.get(book_id, 0) + rec['score'] * 0.4
            
            # 内容过滤权重 0.4
            for rec in content_recs:
                book_id = rec['book_id']
                hybrid_scores[book_id] = hybrid_scores.get(book_id, 0) + rec['score'] * 0.4
            
            # 流行度权重 0.2
            for rec in popularity_recs:
                book_id = rec['book_id']
                hybrid_scores[book_id] = hybrid_scores.get(book_id, 0) + rec['score'] * 0.2
            
            # 排序并返回推荐
            sorted_recommendations = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
            return self._format_recommendations(sorted_recommendations[:num_recommendations], 'hybrid')
            
        except Exception as e:
            print(f"混合推荐失败: {e}")
            return self._popularity_recommendations(num_recommendations)
    
    def _format_recommendations(self, recommendations, method):
        """格式化推荐结果"""
        formatted_recs = []
        
        for book_id, score in recommendations:
            book_info = self.db.get_book_info(book_id)
            if book_info:
                formatted_recs.append({
                    'book_id': book_id,
                    'title': book_info['title'],
                    'author': book_info['author'],
                    'category': book_info['category'],
                    'description': book_info['description'],
                    'score': round(float(score), 3),
                    'method': method
                })
        
        return formatted_recs
    
    def get_similar_books(self, book_id, num_similar=5):
        """获取相似图书"""
        if self.content_similarity_matrix is None:
            return []
        
        try:
            book_idx = list(self.db.books_df['book_id']).index(book_id)
            similarities = self.content_similarity_matrix[book_idx]
            
            # 获取最相似的书籍（排除自己）
            similar_indices = np.argsort(similarities)[::-1][1:num_similar+1]
            similar_books = []
            
            for idx in similar_indices:
                similar_book_id = self.db.books_df.iloc[idx]['book_id']
                book_info = self.db.get_book_info(similar_book_id)
                if book_info:
                    similar_books.append({
                        'book_id': similar_book_id,
                        'title': book_info['title'],
                        'author': book_info['author'],
                        'category': book_info['category'],
                        'similarity': round(float(similarities[idx]), 3)
                    })
            
            return similar_books
            
        except (ValueError, IndexError) as e:
            print(f"获取相似图书失败: {e}")
            return []
    
    def explain_recommendation(self, user_id, book_id):
        """解释推荐原因"""
        explanation = {
            'book_id': book_id,
            'reasons': []
        }
        
        book_info = self.db.get_book_info(book_id)
        if not book_info:
            return explanation
        
        user_ratings = self.db.get_user_ratings(user_id)
        user_profile = self.db.get_user_profile(user_id)
        
        # 基于用户兴趣的解释
        if user_profile and 'interests' in user_profile:
            user_interests = user_profile['interests'].split(',')
            if book_info['category'] in user_interests:
                explanation['reasons'].append(f"您对{book_info['category']}类书籍感兴趣")
        
        # 基于评分历史的解释
        if not user_ratings.empty:
            rated_books = user_ratings.merge(self.db.books_df, on='book_id')
            
            # 相同类别的高分书籍
            same_category_high_rated = rated_books[
                (rated_books['category'] == book_info['category']) & 
                (rated_books['rating'] >= 4)
            ]
            
            if not same_category_high_rated.empty:
                explanation['reasons'].append(
                    f"您曾给{book_info['category']}类的{len(same_category_high_rated)}本书籍打过高分"
                )
            
            # 相同作者的书籍
            same_author_books = rated_books[rated_books['author'] == book_info['author']]
            if not same_author_books.empty:
                avg_rating = same_author_books['rating'].mean()
                explanation['reasons'].append(
                    f"您对作者{book_info['author']}的作品平均评分为{avg_rating:.1f}"
                )
        
        # 基于流行度的解释
        book_ratings = self.db.get_book_ratings(book_id)
        if not book_ratings.empty:
            avg_rating = book_ratings['rating'].mean()
            rating_count = len(book_ratings)
            explanation['reasons'].append(
                f"这本书获得了{rating_count}位读者的平均{avg_rating:.1f}分评价"
            )
        
        return explanation