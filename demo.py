#!/usr/bin/env python3
"""
图书馆智能推荐系统演示脚本
"""

import requests
import json
import time

def demo_recommendation_system():
    """演示推荐系统功能"""
    
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("图书馆智能推荐系统演示")
    print("=" * 60)
    
    # 1. 访问首页
    print("\n1. 访问首页...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✓ 首页访问成功")
        else:
            print(f"✗ 首页访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return
    
    # 2. 用户注册
    print("\n2. 用户注册...")
    register_data = {
        'username': 'demo_user',
        'email': 'demo@example.com',
        'password': 'demo123',
        'confirm_password': 'demo123'
    }
    
    try:
        response = requests.post(f"{base_url}/register", data=register_data)
        if response.status_code == 200:
            print("✓ 用户注册成功")
        else:
            print(f"✗ 用户注册失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 注册请求失败: {e}")
    
    # 3. 用户登录
    print("\n3. 用户登录...")
    login_data = {
        'username': 'test_user',
        'password': 'test123'
    }
    
    try:
        session = requests.Session()
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            print("✓ 用户登录成功")
        else:
            print(f"✗ 用户登录失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 登录请求失败: {e}")
    
    # 4. 浏览图书
    print("\n4. 浏览图书...")
    try:
        response = session.get(f"{base_url}/books")
        if response.status_code == 200:
            print("✓ 图书浏览成功")
        else:
            print(f"✗ 图书浏览失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 浏览请求失败: {e}")
    
    # 5. 获取推荐
    print("\n5. 获取个性化推荐...")
    try:
        response = session.get(f"{base_url}/api/recommendations?algorithm=hybrid&n=5")
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✓ 获取到 {len(recommendations)} 条推荐")
            for i, book in enumerate(recommendations[:3], 1):
                print(f"   {i}. {book.get('title', 'N/A')} - {book.get('author', 'N/A')}")
        else:
            print(f"✗ 推荐获取失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 推荐请求失败: {e}")
    
    # 6. 查看用户中心
    print("\n6. 查看用户中心...")
    try:
        response = session.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print("✓ 用户中心访问成功")
        else:
            print(f"✗ 用户中心访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 用户中心请求失败: {e}")
    
    # 7. 查看管理员统计
    print("\n7. 查看管理员统计...")
    try:
        response = session.get(f"{base_url}/admin/stats")
        if response.status_code == 200:
            print("✓ 管理员统计访问成功")
        else:
            print(f"✗ 管理员统计访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 统计请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n系统功能总结：")
    print("✓ 用户注册和登录")
    print("✓ 图书浏览和搜索")
    print("✓ 个性化推荐")
    print("✓ 用户中心")
    print("✓ 管理员统计")
    print("\n访问地址：")
    print(f"主页: {base_url}")
    print(f"图书浏览: {base_url}/books")
    print(f"用户中心: {base_url}/dashboard")
    print(f"管理员统计: {base_url}/admin/stats")

def test_recommendation_algorithms():
    """测试不同的推荐算法"""
    
    base_url = "http://localhost:5000"
    
    print("\n" + "=" * 60)
    print("推荐算法测试")
    print("=" * 60)
    
    algorithms = ['collaborative', 'content', 'matrix', 'hybrid']
    
    session = requests.Session()
    
    # 先登录
    login_data = {'username': 'test_user', 'password': 'test123'}
    session.post(f"{base_url}/login", data=login_data)
    
    for algorithm in algorithms:
        print(f"\n测试 {algorithm} 推荐算法...")
        try:
            response = session.get(f"{base_url}/api/recommendations?algorithm={algorithm}&n=3")
            if response.status_code == 200:
                recommendations = response.json()
                print(f"✓ {algorithm} 算法返回 {len(recommendations)} 条推荐")
                for i, book in enumerate(recommendations, 1):
                    print(f"   {i}. {book.get('title', 'N/A')}")
            else:
                print(f"✗ {algorithm} 算法失败: {response.status_code}")
        except Exception as e:
            print(f"✗ {algorithm} 算法异常: {e}")
        
        time.sleep(1)  # 避免请求过快

if __name__ == '__main__':
    try:
        demo_recommendation_system()
        test_recommendation_algorithms()
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")