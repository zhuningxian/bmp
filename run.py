#!/usr/bin/env python3
"""
图书馆智能推荐系统启动脚本
便捷的系统启动和管理工具
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: Python {sys.version}")
        sys.exit(1)

def install_dependencies():
    """安装项目依赖"""
    print("正在安装项目依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        sys.exit(1)

def setup_data():
    """初始化数据"""
    print("正在初始化数据...")
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✅ 数据目录创建完成")
    
    # 检查是否已有数据文件
    data_files = ['users.csv', 'books.csv', 'ratings.csv', 'borrowings.csv']
    if all(os.path.exists(f'data/{file}') for file in data_files):
        print("✅ 数据文件已存在")
    else:
        print("📊 数据文件将在首次运行时自动生成")

def run_server(host='0.0.0.0', port=5000, debug=True):
    """启动Flask服务器"""
    print(f"正在启动服务器...")
    print(f"🌐 访问地址: http://{host}:{port}")
    print("🔧 调试模式: 已启用" if debug else "🔧 调试模式: 已禁用")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 设置环境变量
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development' if debug else 'production'
        
        # 导入并运行应用
        from app import app
        app.run(host=host, port=port, debug=debug)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已正确安装")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

def check_dependencies():
    """检查依赖是否已安装"""
    required_packages = [
        'flask', 'pandas', 'numpy', 'scikit-learn', 
        'matplotlib', 'seaborn', 'flask-cors'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图书馆智能推荐系统')
    parser.add_argument('--install', action='store_true', help='安装依赖包')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口 (默认: 5000)')
    parser.add_argument('--no-debug', action='store_true', help='禁用调试模式')
    parser.add_argument('--check', action='store_true', help='检查环境和依赖')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏛️  图书馆智能推荐系统")
    print("   基于用户行为的个性化推荐")
    print("=" * 60)
    
    # 检查Python版本
    check_python_version()
    
    # 如果指定了检查选项
    if args.check:
        print("🔍 正在检查系统环境...")
        check_dependencies()
        setup_data()
        print("✅ 环境检查完成")
        return
    
    # 如果指定了安装选项
    if args.install:
        install_dependencies()
        return
    
    # 检查依赖
    if not check_dependencies():
        print("提示: 运行 'python run.py --install' 来安装依赖")
        return
    
    # 初始化数据
    setup_data()
    
    # 启动服务器
    run_server(
        host=args.host,
        port=args.port,
        debug=not args.no_debug
    )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 运行时错误: {e}")
        sys.exit(1)