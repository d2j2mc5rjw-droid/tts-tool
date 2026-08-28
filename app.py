#!/usr/bin/env python3
"""TTS 语音合成工具 v2.0 - 支持多模型"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import threading
import os
import json

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".tts_config.json")

# TTS 引擎配置
ENGINES = {
    "edge-tts (云端快速)": {
        "type": "edge",
        "voices": {
            "中文女声 - 晓晓": "zh-CN-XiaoxiaoNeural",
            "中文男声 - 云扬": "zh-CN-YunyangNeural",
            "中文女声2 - 晓梦": "zh-CN-XiaomengNeural",
            "英文女声 - Jenny": "en-US-JennyNeural",
            "英文男声 - Guy": "en-US-GuyNeural",
        }
    },
    "edge-tts (云端完整)": {
        "type": "edge_full",
        "voices": {
            "中文女声 - 晓晓": "zh-CN-XiaoxiaoNeural",
            "中文男声 - 云扬": "zh-CN-YunyangNeural",
            "中文女声2 - 晓梦": "zh-CN-XiaomengNeural",
            "中文男声3 - 云健": "zh-CN-YunjianNeural",
            "英文女声 - Jenny": "en-US-JennyNeural",
            "英文男声 - Guy": "en-US-GuyNeural",
            "英文女声 - Aria": "en-US-AriaNeural",
            "日文女声 - Nanami": "ja-JP-NanamiNeural",
        }
    }
}

TEXT_EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.log', '.ini', '.cfg', '.yaml', '.yml']

class TTSApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TTS 语音合成工具 v2.0")
        self.root.geometry("700x650")
        self.root.minsize(600, 550)
        
        self.config = self.load_config()
        self.advanced_mode = tk.BooleanVar(value=False)
        self.loaded_file = None
        
        self.setup_ui()
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {"save_path": os.path.expanduser("~/Desktop"), "engine": list(ENGINES.keys())[0], "voice": ""}
    
    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(main_frame, text="TTS 语音合成工具 v2.0", font=("Helvetica", 16, "bold")).pack(pady=(0, 15))
        
        # 引擎选择
        engine_frame = ttk.LabelFrame(main_frame, text="选择引擎", padding="10")
        engine_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.engine_var = tk.StringVar(value=self.config.get("engine", list(ENGINES.keys())[0]))
        self.engine_var.trace_add("write", self.on_engine_change)
        
        for name in ENGINES.keys():
            ttk.Radiobutton(engine_frame, text=name, variable=self.engine_var, value=name).pack(anchor=tk.W)
        
        # 语音选择
        voice_frame = ttk.LabelFrame(main_frame, text="选择语音", padding="10")
        voice_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.voice_var = tk.StringVar()
        self.voice_buttons = []
        
        self.refresh_voices()
        
        # 文件操作区
        file_frame = ttk.LabelFrame(main_frame, text="文本输入（支持拖拽文件）", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        btn_bar = ttk.Frame(file_frame)
        btn_bar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_bar, text="打开文件", command=self.open_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_bar, text="清空", command=self.clear_text).pack(side=tk.LEFT)
        self.file_label = ttk.Label(btn_bar, text="支持 .txt/.md/.csv 等", foreground="gray")
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        self.text_input = tk.Text(file_frame, height=6, wrap=tk.WORD, font=("Helvetica", 11))
        self.text_input.pack(fill=tk.BOTH, expand=True)
        self.text_input.insert("1.0", "你好，欢迎使用语音合成工具！")
        
        # 保存位置
        save_frame = ttk.Frame(main_frame)
        save_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(save_frame, text="保存位置:").pack(side=tk.LEFT)
        self.save_path = tk.StringVar(value=self.config.get("save_path", os.path.expanduser("~/Desktop")))
        ttk.Entry(save_frame, textvariable=self.save_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        ttk.Button(save_frame, text="选择", command=self.choose_save_path).pack(side=tk.LEFT)
        
        # 高级选项
        self.advanced_frame = ttk.LabelFrame(main_frame, text="高级选项", padding="10")
        
        speed_frame = ttk.Frame(self.advanced_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="语速:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=0)
        ttk.Scale(speed_frame, from_=-50, to=50, variable=self.speed_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.speed_label = ttk.Label(speed_frame, text="0%", width=6)
        self.speed_label.pack(side=tk.LEFT)
        self.speed_var.trace_add("write", lambda *a: self.speed_label.config(text=f"{self.speed_var.get()}%"))
        
        vol_frame = ttk.Frame(self.advanced_frame)
        vol_frame.pack(fill=tk.X, pady=5)
        ttk.Label(vol_frame, text="音量:").pack(side=tk.LEFT)
        self.volume_var = tk.IntVar(value=0)
        ttk.Scale(vol_frame, from_=-50, to=50, variable=self.volume_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.volume_label = ttk.Label(vol_frame, text="0%", width=6)
        self.volume_label.pack(side=tk.LEFT)
        self.volume_var.trace_add("write", lambda *a: self.volume_label.config(text=f"{self.volume_var.get()}%"))
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.generate_btn = ttk.Button(btn_frame, text="生成语音", command=self.generate)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="设置", command=self.toggle_advanced).pack(side=tk.LEFT)
        
        # 状态栏
        self.status = ttk.Label(main_frame, text="就绪", foreground="gray")
        self.status.pack(fill=tk.X)
    
    def on_engine_change(self, *args):
        self.refresh_voices()
    
    def refresh_voices(self):
        engine_name = self.engine_var.get()
        engine = ENGINES.get(engine_name, {})
        voices = engine.get("voices", {})
        
        # 清除旧的语音按钮
        for btn in self.voice_buttons:
            btn.destroy()
        self.voice_buttons.clear()
        
        first = True
        for name, voice_id in voices.items():
            btn = ttk.Radiobutton(self.voice_frame if hasattr(self, 'voice_frame') else self.root, text=name, variable=self.voice_var, value=voice_id)
            btn.pack(anchor=tk.W)
            self.voice_buttons.append(btn)
            if first:
                self.voice_var.set(voice_id)
                first = False
    
    def toggle_advanced(self):
        if self.advanced_frame.winfo_viewable():
            self.advanced_frame.pack_forget()
            self.root.geometry("700x650")
        else:
            self.advanced_frame.pack(fill=tk.X, pady=(0, 10))
            self.root.geometry("700x750")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt *.md *.csv *.json *.xml *.html *.log *.ini *.cfg *.yaml *.yml"), ("所有文件", "*.*")]
        )
        if file_path:
            self.load_text_file(file_path)
    
    def load_text_file(self, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in TEXT_EXTENSIONS and ext != '':
                messagebox.showwarning("警告", f"不支持的文件格式: {ext}")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", content)
            self.loaded_file = file_path
            self.file_label.config(text=f"已加载: {os.path.basename(file_path)}", foreground="green")
            self.status.config(text=f"已加载: {os.path.basename(file_path)}", foreground="blue")
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件: {e}")
    
    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.loaded_file = None
        self.file_label.config(text="支持 .txt/.md/.csv 等", foreground="gray")
        self.status.config(text="就绪", foreground="gray")
    
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
        
        voice_id = self.voice_var.get()
        if not voice_id:
            messagebox.showwarning("警告", "请选择语音")
            return
        
        default_name = "output.mp3"
        if self.loaded_file:
            default_name = os.path.splitext(os.path.basename(self.loaded_file))[0] + ".mp3"
        
        file_path = filedialog.asksaveasfilename(
            initialdir=self.save_path.get(),
            defaultextension=".mp3",
            filetypes=[("MP3 文件", "*.mp3"), ("WAV 文件", "*.wav")],
            initialfile=default_name
        )
        
        if not file_path:
            return
        
        self.config["engine"] = self.engine_var.get()
        self.config["voice"] = voice_id
        self.config["save_path"] = os.path.dirname(file_path)
        self.save_config()
        
        self.generate_btn.config(state="disabled")
        self.status.config(text="生成中...", foreground="blue")
        self.root.update()
        
        engine_type = ENGINES[self.engine_var.get()]["type"]
        thread = threading.Thread(target=self._generate_thread, args=(text, voice_id, file_path, engine_type), daemon=True)
        thread.start()
    
    def _generate_thread(self, text, voice_id, file_path, engine_type):
        try:
            if engine_type in ("edge", "edge_full"):
                self._generate_edge(text, voice_id, file_path)
            self.root.after(0, lambda: self._on_success(file_path))
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))
    
    def _generate_edge(self, text, voice_id, file_path):
        import asyncio
        import edge_tts
        
        async def _gen():
            rate = f"+{self.speed_var.get()}%" if self.speed_var.get() >= 0 else f"{self.speed_var.get()}%"
            volume = f"+{self.volume_var.get()}%" if self.volume_var.get() >= 0 else f"{self.volume_var.get()}%"
            communicate = edge_tts.Communicate(text, voice_id, rate=rate, volume=volume)
            await communicate.save(file_path)
        
        asyncio.run(_gen())
    
    def _on_success(self, file_path):
        self.generate_btn.config(state="normal")
        self.status.config(text="生成成功!", foreground="green")
        messagebox.showinfo("成功", f"语音已保存到:\n{file_path}")
    
    def _on_error(self, error):
        self.generate_btn.config(state="normal")
        self.status.config(text="生成失败", foreground="red")
        messagebox.showerror("错误", f"生成失败:\n{error}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TTSApp()
    app.run()