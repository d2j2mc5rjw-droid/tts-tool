@echo off
REM 构建脚本 (Windows)

echo === TTS 语音合成工具 构建脚本 ===

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 python
    exit /b 1
)

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt
pip install pyinstaller

REM 创建输出目录
if not exist dist mkdir dist

REM 构建
echo 构建中...
pyinstaller --onefile --windowed --name "TTS语音合成工具" app.py

echo 构建完成!
echo 可执行文件: dist\TTS语音合成工具.exe
pause
