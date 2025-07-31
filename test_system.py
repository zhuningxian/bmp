#!/usr/bin/env python3
"""
智能图书馆推荐系统测试脚本
"""

import requests
import json
import time
from datetime import datetime

class LibrarySystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_homepage(self):
        """测试首页"""
        print("测试首页...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ 首页访问成功")
                return True
            else:
                print(f"❌ 首页访问失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 首页访问异常: {e}")
            return False
    
    def test_books_page(self):
        """测试图书页面"""
        print("测试图书页面...")
        try:
            response = self.session.get(f"{self.base_url}/books")
            if response.status_code == 200:
                print("✅ 图书页面访问成功")
                return True
            else:
                print(f"❌ 图书页面访问失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 图书页面访问异常: {e}")
            return False
    
    def test_search_api(self):
        """测试搜索API"""
        print("测试搜索API...")
        try:
            response = self.session.get(f"{self.base_url}/api/search_books", params={"q": "Python"})
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ 搜索API成功，找到 {len(data.get('books', []))} 本图书")
                    return True
                else:
                    print(f"❌ 搜索API返回错误: {data.get('error')}")
                    return False
            else:
                print(f"❌ 搜索API请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 搜索API异常: {e}")
            return False
    
    def test_login_page(self):
        """测试登录页面"""
        print("测试登录页面...")
        try:
            response = self.session.get(f"{self.base_url}/login")
            if response.status_code == 200:
                print("✅ 登录页面访问成功")
                return True
            else:
                print(f"❌ 登录页面访问失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 登录页面访问异常: {e}")
            return False
    
    def test_register_page(self):
        """测试注册页面"""
        print("测试注册页面...")
        try:
            response = self.session.get(f"{self.base_url}/register")
            if response.status_code == 200:
                print("✅ 注册页面访问成功")
                return True
            else:
                print(f"❌ 注册页面访问失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 注册页面访问异常: {e}")
            return False
    
    def test_data_generation(self):
        """测试数据生成"""
        print("测试数据生成...")
        try:
            response = self.session.get(f"{self.base_url}/admin/generate_data")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ 数据生成成功")
                    return True
                else:
                    print(f"❌ 数据生成失败: {data.get('error')}")
                    return False
            else:
                print(f"❌ 数据生成请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 数据生成异常: {e}")
            return False
    
    def test_recommendation_api(self):
        """测试推荐API（需要登录）"""
        print("测试推荐API...")
        try:
            response = self.session.get(f"{self.base_url}/api/recommendations")
            if response.status_code == 302:  # 重定向到登录页面
                print("✅ 推荐API正确重定向到登录页面")
                return True
            elif response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ 推荐API成功，返回 {len(data.get('recommendations', []))} 个推荐")
                    return True
                else:
                    print(f"❌ 推荐API返回错误: {data.get('error')}")
                    return False
            else:
                print(f"❌ 推荐API请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 推荐API异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("智能图书馆推荐系统测试")
        print("=" * 50)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试地址: {self.base_url}")
        print("-" * 50)
        
        tests = [
            ("首页访问", self.test_homepage),
            ("图书页面", self.test_books_page),
            ("搜索API", self.test_search_api),
            ("登录页面", self.test_login_page),
            ("注册页面", self.test_register_page),
            ("数据生成", self.test_data_generation),
            ("推荐API", self.test_recommendation_api),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                results.append((test_name, False))
            time.sleep(1)  # 避免请求过快
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("测试结果汇总")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print("-" * 50)
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有测试通过！系统运行正常。")
        else:
            print("⚠️  部分测试失败，请检查系统配置。")
        
        return passed == total

def main():
    """主函数"""
    tester = LibrarySystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 系统测试完成，可以开始使用了！")
        print("访问地址: http://localhost:5000")
    else:
        print("\n🔧 请检查系统配置并重新运行测试。")

if __name__ == '__main__':
    main()