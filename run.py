#!/usr/bin/env python3
"""
智能图书馆推荐系统启动脚本
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
        print("数据库表创建完成")
        
        # 检查是否需要生成示例数据
        user_count = db.session.query(db.func.count(User.id)).scalar()
        if user_count == 0:
            print("检测到空数据库，正在生成示例数据...")
            generator = DataGenerator()
            generator.generate_all_data()
            print("示例数据生成完成！")
        else:
            print(f"数据库已存在 {user_count} 个用户，跳过示例数据生成")

def main():
    """主函数"""
    print("=" * 50)
    print("智能图书馆推荐系统")
    print("=" * 50)
    
    # 初始化数据库
    init_database()
    
    print("\n启动Web服务器...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()