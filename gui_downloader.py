"""
百度照片批量下载器 - GUI版本
使用tkinter创建图形用户界面
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from myself.down_all.fid_downloader import FidDownloader
from myself.down_all.config_loader import load_cookies_from_settings


class BaiduPhotoDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("百度照片批量下载器")
        self.root.geometry("800x700")
        
        # 下载器实例
        self.downloader = None
        self.download_thread = None
        self.is_downloading = False
        self.is_paused = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置框架
        config_frame = ttk.LabelFrame(main_frame, text="配置选项", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Cookie配置
        ttk.Label(config_frame, text="Cookie文件路径:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cookie_path_var = tk.StringVar(value="settings.json")
        cookie_entry = ttk.Entry(config_frame, textvariable=self.cookie_path_var, width=50)
        cookie_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(config_frame, text="浏览", command=self.browse_cookie).grid(row=0, column=2, pady=2)
        
        # 下载目录
        ttk.Label(config_frame, text="下载目录:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.download_dir_var = tk.StringVar(value="W:/test-picture/test1")
        dir_entry = ttk.Entry(config_frame, textvariable=self.download_dir_var, width=50)
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(config_frame, text="浏览", command=self.browse_download_dir).grid(row=1, column=2, pady=2)
        
        # 最大下载数量
        ttk.Label(config_frame, text="最大下载数量 (-1为全部):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.max_items_var = tk.StringVar(value="3000")
        ttk.Entry(config_frame, textvariable=self.max_items_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=(5, 5), pady=2)
        
        # 更新items信息列表选项
        self.update_fid_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="更新items信息列表（删除旧列表后全量重新获取）", variable=self.update_fid_var).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 试运行选项
        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="试运行模式（仅获取fid列表）", variable=self.dry_run_var).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="开始下载", command=self.start_download)
        self.start_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.pause_btn = ttk.Button(control_frame, text="暂停", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="停止", command=self.stop_download, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=2)
        
        # 进度框架
        progress_frame = ttk.LabelFrame(main_frame, text="下载进度", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 主进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 进度标签
        self.progress_label = ttk.Label(progress_frame, text="准备开始...")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # 状态信息
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 状态文本框
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, width=90)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行和列的权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def browse_cookie(self):
        """浏览Cookie文件"""
        file_path = filedialog.askopenfilename(
            title="选择Cookie配置文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.cookie_path_var.set(file_path)
    
    def browse_download_dir(self):
        """浏览下载目录"""
        dir_path = filedialog.askdirectory(title="选择下载目录")
        if dir_path:
            self.download_dir_var.set(dir_path)
    
    def start_download(self):
        """开始下载"""
        if self.is_downloading:
            return
            
        # 验证输入
        download_dir = self.download_dir_var.get()
        if not download_dir or not os.path.exists(download_dir):
            messagebox.showerror("错误", "下载目录不存在，请重新选择")
            return
        
        # 读取cookies
        try:
            cookies = load_cookies_from_settings()
            if not cookies:
                messagebox.showerror("错误", "无法加载cookies，请检查配置文件")
                return
        except Exception as e:
            messagebox.showerror("错误", f"加载cookies失败: {str(e)}")
            return
        
        # 获取参数
        try:
            max_items = int(self.max_items_var.get())
        except ValueError:
            messagebox.showerror("错误", "最大下载数量必须是数字")
            return
        
        # 创建下载器
        try:
            self.downloader = FidDownloader(
                cookies=cookies,
                download_dir=download_dir,
                max_items=max_items,
                dry_run=self.dry_run_var.get(),
                update_fid_list=self.update_fid_var.get()
            )
        except Exception as e:
            messagebox.showerror("错误", f"创建下载器失败: {str(e)}")
            return
        
        # 更新按钮状态
        self.is_downloading = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        # 启动下载线程
        self.download_thread = threading.Thread(target=self.run_download)
        self.download_thread.daemon = True
        self.download_thread.start()
        
        # 更新状态
        self.append_status("开始下载...")
        self.progress_label.config(text="正在下载...")
    
    def run_download(self):
        """运行下载（在单独线程中）"""
        try:
            # 重定向输出到状态框
            self.downloader.logger.handlers.clear()  # 清除现有处理器
            
            # 由于FidDownloader使用logger，我们需要捕获日志
            self.append_status("下载器已初始化，开始获取fid列表...")
            
            # 直接调用下载方法
            self.downloader.download_all()
            
            self.append_status("下载完成！")
            
        except Exception as e:
            self.append_status(f"下载出错: {str(e)}")
        finally:
            # 下载完成后的处理
            self.root.after(0, self.download_finished)
    
    def toggle_pause(self):
        """切换暂停状态"""
        if not self.downloader:
            return
            
        self.is_paused = not self.is_paused
        self.downloader.toggle_pause()
        
        if self.is_paused:
            self.pause_btn.config(text="继续")
            self.append_status("下载已暂停")
        else:
            self.pause_btn.config(text="暂停")
            self.append_status("下载已继续")
    
    def stop_download(self):
        """停止下载"""
        if self.downloader:
            self.downloader.should_stop = True
            self.append_status("正在停止下载...")
        
        self.download_finished()
    
    def download_finished(self):
        """下载完成后的处理"""
        self.is_downloading = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.pause_btn.config(text="暂停")
        self.progress_label.config(text="下载已完成")
        
        if self.is_paused:
            self.is_paused = False
    
    def append_status(self, message):
        """添加状态消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        def update_text():
            self.status_text.insert(tk.END, formatted_message)
            self.status_text.see(tk.END)  # 滚动到底部
        
        # 确保在主线程中更新GUI
        self.root.after(0, update_text)


def main():
    root = tk.Tk()
    app = BaiduPhotoDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()