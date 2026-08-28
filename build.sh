#!/bin/bash
# 构建脚本

set -e

echo "=== TTS 语音合成工具 构建脚本 ==="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
pip3 install -r requirements.txt
pip3 install pyinstaller

# 创建输出目录
mkdir -p dist

# 构建
echo "构建中..."
pyinstaller --onefile --windowed --name "TTS语音合成工具" app.py

echo "构建完成!"
echo "可执行文件: dist/TTS语音合成工具"
