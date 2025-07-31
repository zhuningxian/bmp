#!/usr/bin/env python3
"""
图书馆智能推荐系统初始化脚本
"""

import os
import sys
from app import app, db
from data_generator import DataGenerator

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✓ 数据库表创建完成")
        
        # 检查是否已有数据
        from models import User, Book, Borrowing, Rating, UserBehavior
        
        user_count = User.query.count()
        book_count = Book.query.count()
        
        if user_count == 0 and book_count == 0:
            print("数据库为空，正在生成测试数据...")
            generator = DataGenerator()
            generator.generate_all_data()
            print("✓ 测试数据生成完成")
        else:
            print(f"数据库已有数据：{user_count} 个用户，{book_count} 本图书")
            choice = input("是否重新生成测试数据？(y/N): ")
            if choice.lower() == 'y':
                print("正在清空数据库...")
                db.drop_all()
                db.create_all()
                print("正在生成新的测试数据...")
                generator = DataGenerator()
                generator.generate_all_data()
                print("✓ 测试数据重新生成完成")

def check_dependencies():
    """检查依赖包"""
    print("正在检查依赖包...")
    
    required_packages = [
        'flask', 'pandas', 'numpy', 'scikit-learn', 'scipy',
        'matplotlib', 'seaborn', 'plotly', 'dash', 'flask-sqlalchemy',
        'flask-login', 'werkzeug', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (缺失)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少以下依赖包：{', '.join(missing_packages)}")
        print("请运行以下命令安装：")
        print("pip install -r requirements.txt")
        return False
    
    print("✓ 所有依赖包检查完成")
    return True

def create_directories():
    """创建必要的目录"""
    print("正在创建目录结构...")
    
    directories = [
        'static/css',
        'static/js',
        'templates',
        'uploads',
        'logs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录：{directory}")
        else:
            print(f"✓ 目录已存在：{directory}")

def show_system_info():
    """显示系统信息"""
    print("\n" + "="*50)
    print("图书馆智能推荐系统")
    print("="*50)
    print("系统特性：")
    print("- 基于协同过滤的推荐算法")
    print("- 基于内容的推荐算法")
    print("- 矩阵分解推荐算法")
    print("- 混合推荐策略")
    print("- 用户行为分析")
    print("- 实时推荐更新")
    print("- 响应式Web界面")
    print("- 数据可视化")
    print("\n技术栈：")
    print("- 后端：Flask + SQLAlchemy")
    print("- 前端：Bootstrap 5 + JavaScript")
    print("- 机器学习：scikit-learn")
    print("- 数据库：SQLite")
    print("- 可视化：Chart.js")
    print("="*50)

def main():
    """主函数"""
    print("图书馆智能推荐系统初始化程序")
    print("="*40)
    
    # 显示系统信息
    show_system_info()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 初始化数据库
    try:
        init_database()
    except Exception as e:
        print(f"数据库初始化失败：{e}")
        sys.exit(1)
    
    print("\n" + "="*40)
    print("系统初始化完成！")
    print("="*40)
    print("启动系统：")
    print("python app.py")
    print("\n访问地址：")
    print("http://localhost:5000")
    print("\n管理员功能：")
    print("http://localhost:5000/admin/stats")
    print("http://localhost:5000/admin/generate-data")

if __name__ == '__main__':
    main()