from flask import Flask, render_template, jsonify
from flask_cors import CORS
from api.recommendation_api import recommendation_bp
from models.database import create_tables
import os

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'library-recommendation-system')
    app.config['DEBUG'] = True
    
    # 启用CORS
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(recommendation_bp, url_prefix='/api')
    
    # 创建数据库表
    create_tables()
    
    # 主页路由
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    @app.route('/user/<int:user_id>')
    def user_page(user_id):
        """用户页面"""
        return render_template('user.html', user_id=user_id)
    
    @app.route('/book/<int:book_id>')
    def book_page(book_id):
        """图书详情页面"""
        return render_template('book.html', book_id=book_id)
    
    @app.route('/search')
    def search_page():
        """搜索页面"""
        return render_template('search.html')
    
    @app.route('/analytics')
    def analytics_page():
        """分析页面"""
        return render_template('analytics.html')
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'status': 'error', 'message': '页面未找到'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 图书馆智能推荐系统启动中...")
    print("📚 访问地址: http://localhost:5000")
    print("🔍 API文档: http://localhost:5000/api")
    app.run(host='0.0.0.0', port=5000, debug=True)