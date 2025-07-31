#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def demo_recommendation_system():
    """演示图书馆智能推荐系统功能"""
    base_url = "http://localhost:5000/api"
    
    print("🎯 图书馆智能推荐系统 - 功能演示")
    print("=" * 50)
    
    # 1. 测试热门图书API
    print("\n1️⃣ 热门图书推荐:")
    try:
        response = requests.get(f"{base_url}/popular?limit=5")
        data = response.json()
        
        if data['status'] == 'success':
            for i, book in enumerate(data['popular_books'], 1):
                print(f"   {i}. 《{book['title']}》 - {book['author']} (热度: {book['popularity_score']})")
        else:
            print("   获取热门图书失败")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 2. 测试用户推荐API
    print("\n2️⃣ 个性化推荐 (用户ID: 1):")
    try:
        response = requests.get(f"{base_url}/recommendations/1?type=adaptive&limit=5")
        data = response.json()
        
        if data['status'] == 'success' and data['recommendations']:
            for i, book in enumerate(data['recommendations'], 1):
                print(f"   {i}. 《{book['title']}》 - {book['author']} (推荐度: {book['recommendation_score']:.3f})")
        else:
            print("   暂无推荐结果")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 3. 测试搜索API
    print("\n3️⃣ 图书搜索 (关键词: '计算机'):")
    try:
        response = requests.get(f"{base_url}/search?q=计算机&limit=3")
        data = response.json()
        
        if data['status'] == 'success' and data['results']:
            for i, book in enumerate(data['results'], 1):
                print(f"   {i}. 《{book['title']}》 - {book['author']} (相关度: {book['relevance_score']})")
        else:
            print("   未找到相关图书")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 4. 测试相似图书API
    print("\n4️⃣ 相似图书推荐 (图书ID: 1):")
    try:
        response = requests.get(f"{base_url}/books/1/recommendations?limit=3")
        data = response.json()
        
        if data['status'] == 'success':
            book_info = data['book']
            print(f"   原图书: 《{book_info['title']}》")
            print(f"   相似图书:")
            for i, book in enumerate(data['similar_books'], 1):
                print(f"     {i}. 《{book['title']}》 (相似度: {book['similarity_score']:.3f})")
        else:
            print("   获取相似图书失败")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 5. 测试分类API
    print("\n5️⃣ 图书分类:")
    try:
        response = requests.get(f"{base_url}/categories")
        data = response.json()
        
        if data['status'] == 'success':
            categories = data['categories']
            print(f"   可用分类: {', '.join(categories)}")
        else:
            print("   获取分类失败")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 6. 测试推荐解释API
    print("\n6️⃣ 推荐原因解释 (用户1, 图书9):")
    try:
        response = requests.get(f"{base_url}/recommendations/1/9/explain")
        data = response.json()
        
        if data['status'] == 'success':
            explanations = data['explanations']
            for i, explanation in enumerate(explanations, 1):
                print(f"   {i}. {explanation}")
        else:
            print("   无法获取推荐解释")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 7. 测试评分添加API
    print("\n7️⃣ 添加图书评分:")
    try:
        rating_data = {
            "book_id": 1,
            "rating": 5,
            "review": "非常好的Python入门书籍！"
        }
        
        response = requests.post(
            f"{base_url}/users/1/rating",
            json=rating_data,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['status'] == 'success':
            print("   ✅ 评分添加成功")
        else:
            print(f"   ❌ 评分添加失败: {data['message']}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n🎉 演示完成！")
    print("\n📝 系统特性总结:")
    print("   ✓ 多种推荐算法 (协同过滤、内容过滤、混合推荐)")
    print("   ✓ 个性化推荐")
    print("   ✓ 图书搜索和分类")
    print("   ✓ 相似图书发现") 
    print("   ✓ 推荐原因解释")
    print("   ✓ 用户评分系统")
    print("   ✓ 热门图书统计")
    
    print(f"\n🌐 访问 http://localhost:5000 体验完整的Web界面")

if __name__ == "__main__":
    print("等待服务器启动...")
    time.sleep(2)  # 等待服务器启动
    demo_recommendation_system()