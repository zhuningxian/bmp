#!/usr/bin/env python3
"""
API测试脚本
"""

import requests
import json

def test_api_endpoints():
    """测试API端点"""
    
    base_url = "http://localhost:5000"
    
    print("API端点测试")
    print("=" * 50)
    
    # 1. 测试登录
    print("1. 测试登录...")
    session = requests.Session()
    
    login_data = {
        'username': 'demo_user',
        'password': 'demo123'
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        if response.status_code == 200:
            print("✓ 登录成功")
        else:
            print("✗ 登录失败")
            print(f"响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"登录异常: {e}")
        return
    
    # 2. 测试推荐API
    print("\n2. 测试推荐API...")
    
    algorithms = ['collaborative', 'content', 'matrix', 'hybrid']
    
    for algorithm in algorithms:
        print(f"\n测试 {algorithm} 算法...")
        try:
            response = session.get(f"{base_url}/api/recommendations?algorithm={algorithm}&n=3")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 成功获取 {len(data)} 条推荐")
                for i, book in enumerate(data[:2], 1):
                    print(f"   {i}. {book.get('title', 'N/A')}")
            else:
                print(f"✗ 请求失败")
                print(f"响应内容: {response.text[:300]}")
                
        except Exception as e:
            print(f"✗ 异常: {e}")
    
    # 3. 测试其他API
    print("\n3. 测试其他API...")
    
    apis = [
        ("/", "首页"),
        ("/books", "图书列表"),
        ("/dashboard", "用户中心"),
        ("/admin/stats", "管理员统计")
    ]
    
    for route, name in apis:
        try:
            response = session.get(f"{base_url}{route}")
            print(f"{name}: {response.status_code}")
        except Exception as e:
            print(f"{name}: 异常 - {e}")

if __name__ == '__main__':
    test_api_endpoints()