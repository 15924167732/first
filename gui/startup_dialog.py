"""
FF14战斗分析器 - 启动配置对话框
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


class StartupConfigDialog:
    """启动配置对话框"""
    
    def __init__(self, config):
        """初始化对话框
        
        Args:
            config: Config配置对象
        """
        self.config = config
        self.result = None  # 用户的选择结果
        
        # 创建对话框窗口
        self.dialog = tk.Tk()
        self.dialog.title("ACT启动配置")
        self.dialog.geometry("500x300")
        self.dialog.configure(bg="#1e1e1e")
        self.dialog.resizable(False, False)
        
        # 设置窗口图标
        try:
            # 支持打包后的exe
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(os.path.dirname(sys.executable), "Dragoon.png")
            else:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Dragoon.png")
            if os.path.exists(icon_path):
                self.dialog.iconphoto(True, tk.PhotoImage(file=icon_path))
        except:
            pass
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
        
        # 设置窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _center_window(self):
        """窗口居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        tk.Label(
            self.dialog,
            text="ACT 启动设置",
            font=("Microsoft YaHei", 14, "bold"),
            fg="#e6e6e6",
            bg="#1e1e1e"
        ).pack(pady=(20, 30))
        
        # 选项框架
        options_frame = tk.Frame(self.dialog, bg="#1e1e1e")
        options_frame.pack(fill="x", padx=40, pady=10)
        
        # ACT路径选择
        path_frame = tk.Frame(options_frame, bg="#1e1e1e")
        path_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(
            path_frame,
            text="ACT 启动文件:",
            font=("Microsoft YaHei", 10),
            fg="#d6d6d6",
            bg="#1e1e1e"
        ).pack(anchor="w", pady=(0, 5))
        
        path_input_frame = tk.Frame(path_frame, bg="#1e1e1e")
        path_input_frame.pack(fill="x")
        
        self.act_path_entry = tk.Entry(
            path_input_frame,
            font=("Microsoft YaHei", 9),
            fg="#bfbfbf",
            bg="#232323",
            relief="flat"
        )
        self.act_path_entry.pack(side="left", fill="x", expand=True, ipady=6)
        
        # 设置当前路径
        current_path = self.config.get_act_path()
        if current_path:
            self.act_path_entry.insert(0, current_path)
        else:
            # 显示默认路径（相对路径）
            default_path = self._get_default_act_path()
            self.act_path_entry.insert(0, default_path)
            self.act_path_entry.config(fg="#888888")
        
        tk.Button(
            path_input_frame,
            text="浏览...",
            font=("Microsoft YaHei", 9),
            fg="#e6e6e6",
            bg="#2a2a2a",
            relief="flat",
            width=8,
            command=self._browse_act_path
        ).pack(side="left", padx=(10, 0))
        
        # 提示信息
        tk.Label(
            path_frame,
            text="默认为相对路径，也可浏览选择其他 ACT 启动文件",
            font=("Microsoft YaHei", 8),
            fg="#888888",
            bg="#1e1e1e"
        ).pack(anchor="w", pady=(5, 0))
        
        # 按钮框架
        btn_frame = tk.Frame(self.dialog, bg="#1e1e1e")
        btn_frame.pack(pady=30)
        
        tk.Button(
            btn_frame,
            text="启动 ACT",
            font=("Microsoft YaHei", 11),
            fg="#e6e6e6",
            bg="#a960ff",
            relief="flat",
            width=12,
            command=self._on_confirm
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame,
            text="不启动 ACT",
            font=("Microsoft YaHei", 11),
            fg="#e6e6e6",
            bg="#2a2a2a",
            relief="flat",
            width=12,
            command=self._on_cancel
        ).pack(side="left", padx=10)
    
    def _get_default_act_path(self):
        """获取默认ACT路径（相对路径显示）"""
        return os.path.join("ACT.DieMoe", "点我启动ACT.exe")

    
    def _browse_act_path(self):
        """浏览ACT启动文件"""
        # 获取默认初始目录（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            initial_dir = os.path.dirname(sys.executable)
        else:
            initial_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        filename = filedialog.askopenfilename(
            title="选择 ACT 启动文件",
            initialdir=initial_dir,
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        
        if filename:
            self.act_path_entry.config(fg="#bfbfbf")
            self.act_path_entry.delete(0, tk.END)
            self.act_path_entry.insert(0, filename)
    
    def _on_confirm(self):
        """确认按钮 - 启动ACT（使用默认或自定义路径）"""
        # 保存配置：启动ACT
        self.config.set_auto_start_act(True)
        
        # 获取ACT路径
        act_path = self.act_path_entry.get().strip()
        
        # 如果是默认路径（灰色显示的），则保存为空字符串
        if act_path == self._get_default_act_path():
            act_path = ""  # 使用默认路径
        
        self.config.set_act_path(act_path)
        self.config.save_config()
        
        self.result = True
        self.dialog.destroy()
    
    def _on_cancel(self):
        """取消按钮 - 不启动ACT，只启动主程序"""
        # 保存配置：不启动ACT
        self.config.set_auto_start_act(False)
        self.config.save_config()
        
        self.result = True  # 返回True以继续启动主程序
        self.dialog.destroy()
    
    def show(self):
        """显示对话框并等待结果
        
        Returns:
            bool: True表示确认，False表示取消
        """
        self.dialog.mainloop()
        return self.result if self.result is not None else False
