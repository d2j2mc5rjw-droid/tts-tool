# TTS 语音合成工具

一个简单易用的文本转语音工具，支持多种语音。

## 功能特点

- 支持中文和英文语音
- 简单模式和高级模式
- 可调节语速和音量
- 支持选择保存位置
- 配置自动保存

## 安装

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/d2j2mc5rjw-droid/tts-tool.git
cd tts-tool

# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

### 下载安装包

从 [Releases](https://github.com/d2j2mc5rjw-droid/tts-tool/releases) 页面下载对应平台的安装包。

## 使用说明

### 基础模式

1. 输入要转换的文本
2. 选择语音类型
3. 点击"选择"按钮选择保存位置
4. 点击"生成语音"

### 高级模式

点击"设置"按钮可以展开高级选项：
- 语速调节（-50% 到 +50%）
- 音量调节（-50% 到 +50%）

## 可用语音

| 语音 | 语言 | 说明 |
|------|------|------|
| 晓晓 | 中文 | 女声 |
| 云扬 | 中文 | 男声 |
| 晓梦 | 中文 | 女声2 |
| Jenny | 英文 | 女声 |
| Guy | 英文 | 男声 |

## 构建

### Windows
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "TTS语音合成工具" app.py
```

### macOS
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "TTS语音合成工具" app.py
```

### Linux
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "TTS语音合成工具" app.py
```

## 依赖

- Python 3.8+
- edge-tts
- tkinter (Python 内置)

## 许可证

MIT License
