#!/bin/bash

# 智能图书馆推荐系统启动脚本

echo "=================================================="
echo "智能图书馆推荐系统"
echo "=================================================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python版本检查通过: $python_version"
else
    echo "❌ Python版本过低，需要3.8或更高版本"
    exit 1
fi

# 检查pip
if command -v pip3 &> /dev/null; then
    echo "✅ pip检查通过"
else
    echo "❌ pip未安装，请先安装pip"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 检查数据库文件
if [ ! -f "library.db" ]; then
    echo "初始化数据库..."
    python run.py &
    sleep 10
    kill %1
    echo "数据库初始化完成"
fi

# 启动应用
echo "启动Web服务器..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo "=================================================="

python run.py