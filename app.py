#!/usr/bin/env python3
"""TTS 语音合成工具 - GUI 版本（支持拖拽文件）"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import edge_tts
import threading
import os
import sys
import json

# 语音配置
VOICES = {
    "中文女声 - 晓晓": "zh-CN-XiaoxiaoNeural",
    "中文男声 - 云扬": "zh-CN-YunyangNeural",
    "中文女声2 - 晓梦": "zh-CN-XiaomengNeural",
    "英文女声 - Jenny": "en-US-JennyNeural",
    "英文男声 - Guy": "en-US-GuyNeural",
}

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".tts_config.json")

# 支持的文本文件格式
TEXT_EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.log', '.ini', '.cfg', '.yaml', '.yml']

class TTSApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TTS 语音合成工具")
        self.root.geometry("650x600")
        self.root.minsize(550, 500)
        
        # 配置
        self.config = self.load_config()
        self.advanced_mode = tk.BooleanVar(value=False)
        self.loaded_file = None
        
        self.setup_ui()
        self.center_window()
        self.setup_drop()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {"save_path": os.path.expanduser("~/Desktop"), "voice": list(VOICES.keys())[0]}
    
    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def setup_drop(self):
        """设置拖拽支持（使用 TkinterDnD 或回退方案）"""
        try:
            # 尝试使用 tkinterdnd2
            import tkinterdnd2
            self.root.drop_target_register(tkinterdnd2.DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        except ImportError:
            # 回退方案：绑定鼠标事件提示用户
            pass
    
    def on_drop(self, event):
        """处理拖拽文件"""
        files = self.root.tk.splitlist(event.data)
        if files:
            self.load_text_file(files[0])
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title = ttk.Label(main_frame, text="TTS 语音合成工具", font=("Helvetica", 16, "bold"))
        title.pack(pady=(0, 15))
        
        # 文件操作区
        file_frame = ttk.LabelFrame(main_frame, text="文本输入（支持拖拽 .txt 文件）", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 按钮栏
        btn_bar = ttk.Frame(file_frame)
        btn_bar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_bar, text="打开文件", command=self.open_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_bar, text="清空", command=self.clear_text).pack(side=tk.LEFT, padx=(0, 10))
        self.file_label = ttk.Label(btn_bar, text="（可拖拽 .txt 文件到此处）", foreground="gray")
        self.file_label.pack(side=tk.LEFT)
        
        # 文本输入
        self.text_input = tk.Text(file_frame, height=8, wrap=tk.WORD, font=("Helvetica", 11))
        self.text_input.pack(fill=tk.BOTH, expand=True)
        self.text_input.insert("1.0", "你好，欢迎使用语音合成工具！")
        
        # 绑定拖拽事件到文本框
        self.text_input.bind('<Button-1>', self.on_text_click)
        
        # 语音选择
        voice_frame = ttk.LabelFrame(main_frame, text="选择语音", padding="10")
        voice_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.voice_var = tk.StringVar(value=self.config.get("voice", list(VOICES.keys())[0]))
        for name in VOICES.keys():
            ttk.Radiobutton(voice_frame, text=name, variable=self.voice_var, value=name).pack(anchor=tk.W, pady=2)
        
        # 高级选项框架（默认隐藏）
        self.advanced_frame = ttk.LabelFrame(main_frame, text="高级选项", padding="10")
        
        # 语速调节
        speed_frame = ttk.Frame(self.advanced_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="语速:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=0)
        self.speed_scale = ttk.Scale(speed_frame, from_=-50, to=50, variable=self.speed_var, orient=tk.HORIZONTAL)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.speed_label = ttk.Label(speed_frame, text="0%", width=6)
        self.speed_label.pack(side=tk.LEFT)
        self.speed_var.trace_add("write", lambda *args: self.speed_label.config(text=f"{self.speed_var.get()}%"))
        
        # 音量调节
        vol_frame = ttk.Frame(self.advanced_frame)
        vol_frame.pack(fill=tk.X, pady=5)
        ttk.Label(vol_frame, text="音量:").pack(side=tk.LEFT)
        self.volume_var = tk.IntVar(value=0)
        self.volume_scale = ttk.Scale(vol_frame, from_=-50, to=50, variable=self.volume_var, orient=tk.HORIZONTAL)
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.volume_label = ttk.Label(vol_frame, text="0%", width=6)
        self.volume_label.pack(side=tk.LEFT)
        self.volume_var.trace_add("write", lambda *args: self.volume_label.config(text=f"{self.volume_var.get()}%"))
        
        # 保存位置
        save_frame = ttk.Frame(main_frame)
        save_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(save_frame, text="保存位置:", font=("Helvetica", 11)).pack(side=tk.LEFT)
        self.save_path = tk.StringVar(value=self.config.get("save_path", os.path.expanduser("~/Desktop")))
        ttk.Entry(save_frame, textvariable=self.save_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        ttk.Button(save_frame, text="选择", command=self.choose_save_path).pack(side=tk.LEFT)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.generate_btn = ttk.Button(btn_frame, text="生成语音", command=self.generate)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="设置", command=self.toggle_advanced).pack(side=tk.LEFT)
        
        # 状态栏
        self.status = ttk.Label(main_frame, text="就绪", foreground="gray", font=("Helvetica", 10))
        self.status.pack(fill=tk.X)
        
    def on_text_click(self, event):
        """点击文本框时的处理"""
        pass
    
    def open_file(self):
        """打开文本文件"""
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[
                ("文本文件", "*.txt *.md *.csv *.json *.xml *.html *.log *.ini *.cfg *.yaml *.yml"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.load_text_file(file_path)
    
    def load_text_file(self, file_path):
        """加载文本文件"""
        try:
            # 检查文件扩展名
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in TEXT_EXTENSIONS and ext != '':
                messagebox.showwarning("警告", f"不支持的文件格式: {ext}")
                return
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新文本框
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", content)
            
            # 更新文件标签
            self.loaded_file = file_path
            self.file_label.config(text=f"已加载: {os.path.basename(file_path)}", foreground="green")
            
            self.status.config(text=f"已加载文件: {os.path.basename(file_path)}", foreground="blue")
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件: {e}")
    
    def clear_text(self):
        """清空文本"""
        self.text_input.delete("1.0", tk.END)
        self.loaded_file = None
        self.file_label.config(text="（可拖拽 .txt 文件到此处）", foreground="gray")
        self.status.config(text="就绪", foreground="gray")
    
    def toggle_advanced(self):
        if self.advanced_frame.winfo_viewable():
            self.advanced_frame.pack_forget()
            self.advanced_mode.set(False)
            self.root.geometry("650x600")
        else:
            self.advanced_frame.pack(fill=tk.X, pady=(0, 15))
            self.advanced_mode.set(True)
            self.root.geometry("650x700")
    
    def choose_save_path(self):
        path = filedialog.askdirectory(initialdir=self.save_path.get())
        if path:
            self.save_path.set(path)
            self.config["save_path"] = path
            self.save_config()
    
    def generate(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入文本或打开文件")
            return
        
        voice_name = self.voice_var.get()
        voice_id = VOICES[voice_name]
        
        # 选择保存文件
        default_name = "output.mp3"
        if self.loaded_file:
            default_name = os.path.splitext(os.path.basename(self.loaded_file))[0] + ".mp3"
        
        file_path = filedialog.asksaveasfilename(
            initialdir=self.save_path.get(),
            defaultextension=".mp3",
            filetypes=[("MP3 文件", "*.mp3"), ("WAV 文件", "*.wav"), ("所有文件", "*.*")],
            initialfile=default_name
        )
        
        if not file_path:
            return
        
        # 保存配置
        self.config["voice"] = voice_name
        self.config["save_path"] = os.path.dirname(file_path)
        self.save_config()
        
        # 禁用按钮
        self.generate_btn.config(state="disabled")
        self.status.config(text="生成中...", foreground="blue")
        self.root.update()
        
        # 在新线程中生成
        thread = threading.Thread(target=self._generate_thread, args=(text, voice_id, file_path), daemon=True)
        thread.start()
    
    def _generate_thread(self, text, voice_id, file_path):
        try:
            asyncio.run(self._generate_async(text, voice_id, file_path))
            self.root.after(0, lambda: self._on_success(file_path))
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))
    
    def _on_success(self, file_path):
        self.generate_btn.config(state="normal")
        self.status.config(text="生成成功!", foreground="green")
        messagebox.showinfo("成功", f"语音已保存到:\n{file_path}")
    
    def _on_error(self, error):
        self.generate_btn.config(state="normal")
        self.status.config(text="生成失败", foreground="red")
        messagebox.showerror("错误", f"生成失败:\n{error}")
    
    async def _generate_async(self, text, voice_id, file_path):
        rate = f"+{self.speed_var.get()}%" if self.speed_var.get() >= 0 else f"{self.speed_var.get()}%"
        volume = f"+{self.volume_var.get()}%" if self.volume_var.get() >= 0 else f"{self.volume_var.get()}%"
        
        communicate = edge_tts.Communicate(text, voice_id, rate=rate, volume=volume)
        await communicate.save(file_path)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TTSApp()
    app.run()