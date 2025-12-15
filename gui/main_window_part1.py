"""
FF14战斗分析器 - 主窗口GUI（第1部分）
包含基础框架、UI创建和页面切换功能
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analyzer import ACTLogAnalyzer
from core.monitor import RealtimeMonitor
from gui.overlay_window import OverlayWindow
from utils.constants import DEFAULT_LOG_PATH, DEFAULT_OUTPUT_DIR, WINDOW_GEOMETRY


class FF14BattleAnalyzer:
    """FF14战斗分析器主界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("FF14战斗分析器")
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.configure(bg="#121212")
        
        # 数据存储
        self.all_reports = []
        self.selected_fight = None
        self.current_view_type = "damage"
        self.zone_expanded = {}
        self.zone_widgets = {}
        self.imported_log_files = set()
        
        # 悬浮窗
        self.overlay_window = None
        self.current_fight_data = None
        
        # 监控器
        self.monitor = None
        self.is_monitoring = False
        
        # 配置
        self.log_file_path = DEFAULT_LOG_PATH
        self.output_dir = DEFAULT_OUTPUT_DIR
        
        # 主容器
        self.main_frame = tk.Frame(root, bg="#121212")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # 内容区域
        self.content_frame = tk.Frame(self.main_frame, bg="#1e1e1e", bd=1, relief="solid")
        self.content_frame.pack(fill="both", expand=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.create_top_nav()
        self.create_home_page()
        self.create_log_control_page()
        self.show_page("home")
    
    def create_top_nav(self):
        """创建顶部导航"""
        nav_frame = tk.Frame(self.content_frame, bg="#1e1e1e")
        nav_frame.pack(fill="x", padx=40, pady=20)
        
        # 标题
        title_label = tk.Label(
            nav_frame,
            text="FF14战斗分析器",
            font=("Microsoft YaHei", 28, "normal"),
            fg="white",
            bg="#1e1e1e"
        )
        title_label.pack(anchor="w")
        
        # 标签页和按钮容器
        tabs_container = tk.Frame(nav_frame, bg="#1e1e1e")
        tabs_container.pack(anchor="w", pady=(40, 0))
        
        # 标签页区域
        tabs_frame = tk.Frame(tabs_container, bg="#1e1e1e")
        tabs_frame.pack(side="left")
        
        self.tabs = {}
        tab_names = [
            ("主页", "home"),
            ("日志控制", "log_control")
        ]
        
        for i, (name, key) in enumerate(tab_names):
            tab = tk.Frame(
                tabs_frame,
                bg="#a960ff" if key == "home" else "#252525",
                width=180,
                height=40
            )
            tab.pack_propagate(False)
            tab.pack(side="left", padx=(0, 10))
            
            label = tk.Label(
                tab,
                text=name,
                font=("Microsoft YaHei", 12, "normal"),
                fg="#e6e6e6",
                bg=tab.cget("bg"),
                cursor="hand2"
            )
            label.pack(expand=True)
            
            label.bind("<Button-1>", lambda e, k=key: self.show_page(k))
            tab.bind("<Button-1>", lambda e, k=key: self.show_page(k))
            
            self.tabs[key] = (tab, label)
        
        # 悬浮窗按钮
        tk.Button(
            tabs_container,
            text="悬浮窗",
            font=("Microsoft YaHei", 12, "normal"),
            fg="#e6e6e6",
            bg="#4a9eff",
            relief="flat",
            width=12,
            height=1,
            command=self.open_overlay_window
        ).pack(side="left", padx=20)
