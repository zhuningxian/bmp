#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from datetime import datetime, timedelta
from models.database import create_tables, SessionLocal, User, Book, Rating, Borrowing

def init_database():
    """初始化数据库并添加测试数据"""
    print("正在初始化数据库...")
    
    # 创建表
    create_tables()
    print("✓ 数据库表创建完成")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 清除现有数据
        db.query(Rating).delete()
        db.query(Borrowing).delete()
        db.query(Book).delete()
        db.query(User).delete()
        db.commit()
        
        # 添加用户数据
        users_data = [
            {"username": "张三", "email": "zhangsan@example.com", "age": 25, "occupation": "软件工程师"},
            {"username": "李四", "email": "lisi@example.com", "age": 30, "occupation": "教师"},
            {"username": "王五", "email": "wangwu@example.com", "age": 28, "occupation": "医生"},
            {"username": "赵六", "email": "zhaoliu@example.com", "age": 22, "occupation": "学生"},
            {"username": "钱七", "email": "qianqi@example.com", "age": 35, "occupation": "律师"},
            {"username": "孙八", "email": "sunba@example.com", "age": 27, "occupation": "设计师"},
            {"username": "周九", "email": "zhoujiu@example.com", "age": 32, "occupation": "记者"},
            {"username": "吴十", "email": "wushi@example.com", "age": 26, "occupation": "会计"},
            {"username": "郑一", "email": "zhengyi@example.com", "age": 29, "occupation": "研究员"},
            {"username": "王二", "email": "wanger@example.com", "age": 24, "occupation": "程序员"}
        ]
        
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        
        db.commit()
        print("✓ 用户数据添加完成")
        
        # 添加图书数据
        books_data = [
            {
                "isbn": "9787111123456",
                "title": "Python编程：从入门到实践",
                "author": "埃里克·马瑟斯",
                "publisher": "人民邮电出版社",
                "publication_year": 2019,
                "category": "计算机",
                "description": "一本针对所有层次Python读者而作的Python入门书",
                "language": "中文",
                "pages": 459
            },
            {
                "isbn": "9787121234567",
                "title": "深度学习",
                "author": "伊恩·古德费洛",
                "publisher": "电子工业出版社",
                "publication_year": 2017,
                "category": "计算机",
                "description": "深度学习领域的奠基性的经典教材",
                "language": "中文",
                "pages": 692
            },
            {
                "isbn": "9787508345678",
                "title": "百年孤独",
                "author": "加西亚·马尔克斯",
                "publisher": "中信出版社",
                "publication_year": 2011,
                "category": "文学",
                "description": "魔幻现实主义代表作，诺贝尔文学奖作品",
                "language": "中文",
                "pages": 384
            },
            {
                "isbn": "9787020456789",
                "title": "围城",
                "author": "钱钟书",
                "publisher": "人民文学出版社",
                "publication_year": 2010,
                "category": "文学",
                "description": "中国现代文学经典作品",
                "language": "中文",
                "pages": 352
            },
            {
                "isbn": "9787010567890",
                "title": "中国近代史",
                "author": "徐中约",
                "publisher": "世界图书出版公司",
                "publication_year": 2013,
                "category": "历史",
                "description": "权威的中国近代史教材",
                "language": "中文",
                "pages": 896
            },
            {
                "isbn": "9787100678901",
                "title": "史记",
                "author": "司马迁",
                "publisher": "商务印书馆",
                "publication_year": 2015,
                "category": "历史",
                "description": "中国历史学经典巨著",
                "language": "中文",
                "pages": 1200
            },
            {
                "isbn": "9787302789012",
                "title": "算法导论",
                "author": "托马斯·科尔曼",
                "publisher": "清华大学出版社",
                "publication_year": 2012,
                "category": "计算机",
                "description": "计算机算法领域的经典教材",
                "language": "中文",
                "pages": 1024
            },
            {
                "isbn": "9787544890123",
                "title": "时间简史",
                "author": "史蒂芬·霍金",
                "publisher": "译林出版社",
                "publication_year": 2014,
                "category": "科学",
                "description": "探索宇宙奥秘的科普经典",
                "language": "中文",
                "pages": 256
            },
            {
                "isbn": "9787208901234",
                "title": "人类简史",
                "author": "尤瓦尔·赫拉利",
                "publisher": "中信出版社",
                "publication_year": 2017,
                "category": "历史",
                "description": "从动物到上帝的人类发展史",
                "language": "中文",
                "pages": 512
            },
            {
                "isbn": "9787552012345",
                "title": "活着",
                "author": "余华",
                "publisher": "作家出版社",
                "publication_year": 2012,
                "category": "文学",
                "description": "当代中国文学经典作品",
                "language": "中文",
                "pages": 256
            },
            {
                "isbn": "9787111223456",
                "title": "数据结构与算法分析",
                "author": "马克·艾伦·韦斯",
                "publisher": "机械工业出版社",
                "publication_year": 2016,
                "category": "计算机",
                "description": "数据结构和算法分析的权威教材",
                "language": "中文",
                "pages": 598
            },
            {
                "isbn": "9787506334567",
                "title": "红楼梦",
                "author": "曹雪芹",
                "publisher": "作家出版社",
                "publication_year": 2008,
                "category": "文学",
                "description": "中国古典文学四大名著之首",
                "language": "中文",
                "pages": 1280
            },
            {
                "isbn": "9787030445678",
                "title": "相对论",
                "author": "阿尔伯特·爱因斯坦",
                "publisher": "科学出版社",
                "publication_year": 2015,
                "category": "科学",
                "description": "现代物理学基础理论经典",
                "language": "中文",
                "pages": 192
            },
            {
                "isbn": "9787108556789",
                "title": "三体",
                "author": "刘慈欣",
                "publisher": "重庆出版社",
                "publication_year": 2008,
                "category": "科幻",
                "description": "中国科幻小说代表作",
                "language": "中文",
                "pages": 368
            },
            {
                "isbn": "9787544667890",
                "title": "经济学原理",
                "author": "N.格里高利·曼昆",
                "publisher": "北京大学出版社",
                "publication_year": 2018,
                "category": "经济",
                "description": "经济学入门经典教材",
                "language": "中文",
                "pages": 896
            }
        ]
        
        for book_data in books_data:
            book = Book(**book_data)
            db.add(book)
        
        db.commit()
        print("✓ 图书数据添加完成")
        
        # 获取所有用户和图书的ID
        users = db.query(User).all()
        books = db.query(Book).all()
        
        # 添加借阅记录
        print("正在生成借阅记录...")
        borrowings = []
        for _ in range(150):  # 生成150条借阅记录
            user = random.choice(users)
            book = random.choice(books)
            
            # 避免重复借阅
            existing = db.query(Borrowing).filter(
                Borrowing.user_id == user.id,
                Borrowing.book_id == book.id,
                Borrowing.return_date.is_(None)
            ).first()
            
            if not existing:
                borrow_date = datetime.now() - timedelta(days=random.randint(1, 365))
                due_date = borrow_date + timedelta(days=30)
                
                # 70%的图书已归还
                if random.random() < 0.7:
                    return_date = borrow_date + timedelta(days=random.randint(1, 35))
                else:
                    return_date = None
                
                borrowing = Borrowing(
                    user_id=user.id,
                    book_id=book.id,
                    borrow_date=borrow_date,
                    due_date=due_date,
                    return_date=return_date
                )
                borrowings.append(borrowing)
        
        db.add_all(borrowings)
        db.commit()
        print(f"✓ 添加了 {len(borrowings)} 条借阅记录")
        
        # 添加评分记录
        print("正在生成评分记录...")
        ratings = []
        for _ in range(100):  # 生成100条评分记录
            user = random.choice(users)
            book = random.choice(books)
            
            # 避免重复评分
            existing = db.query(Rating).filter(
                Rating.user_id == user.id,
                Rating.book_id == book.id
            ).first()
            
            if not existing:
                rating_score = random.choice([3, 3, 4, 4, 4, 5, 5, 2, 1])  # 偏向高分
                reviews = [
                    "很好的书，推荐阅读",
                    "内容丰富，受益匪浅",
                    "写得不错，值得一读",
                    "经典作品，百读不厌",
                    "很有启发性",
                    "内容深刻，引人思考",
                    "文笔优美，情节生动",
                    "专业性强，学到很多",
                    ""  # 有些评分没有评论
                ]
                
                rating = Rating(
                    user_id=user.id,
                    book_id=book.id,
                    rating=rating_score,
                    review=random.choice(reviews),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 200))
                )
                ratings.append(rating)
        
        db.add_all(ratings)
        db.commit()
        print(f"✓ 添加了 {len(ratings)} 条评分记录")
        
        print("\n🎉 数据库初始化完成！")
        print(f"📊 数据统计:")
        print(f"   用户: {len(users)} 个")
        print(f"   图书: {len(books)} 本")
        print(f"   借阅记录: {len(borrowings)} 条")
        print(f"   评分记录: {len(ratings)} 条")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()