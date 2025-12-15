"""
FF14战斗分析器主窗口
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
from datetime import datetime, timedelta

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
        
        # 获取图标路径（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            self.icon_path = os.path.join(os.path.dirname(sys.executable), "Dragoon.png")
        else:
            self.icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Dragoon.png")
        
        # 数据存储
        self.all_reports = []  # 所有副本报告
        self.selected_fight = None
        self.current_view_type = "damage"  # damage, healing, death
        self.zone_expanded = {}  # 记录每个副本的展开状态
        self.zone_widgets = {}  # 记录每个副本的组件引用 {zone_name: {'header': frame, 'container': frame}}
        self.imported_log_files = set()  # 记录已导入的日志文件的绝对路径
        
        # 悬浮窗
        self.overlay_window = None
        self.current_fight_data = None  # 当前战斗数据
        
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
        
        # 悬浮窗按钮（在标签页右边）
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
    
    def create_home_page(self):
        """创建主页"""
        self.home_page = tk.Frame(self.content_frame, bg="#1e1e1e")
        # 不在这里pack，在show_page时pack
        
        # 监控控制区域（单行布局）
        control_frame = tk.Frame(self.home_page, bg="#181818")
        control_frame.pack(fill="x", padx=40, pady=(40, 20))
        
        # 内容容器
        content_row = tk.Frame(control_frame, bg="#181818")
        content_row.pack(fill="x", padx=20, pady=20)
        
        # 左侧：监控按钮组
        left_section = tk.Frame(content_row, bg="#181818")
        left_section.pack(side="left")
        
        self.start_monitor_btn = tk.Button(
            left_section,
            text="开始实时监控",
            font=("Microsoft YaHei", 12, "normal"),
            fg="#e6e6e6",
            bg="#a960ff",
            relief="flat",
            width=15,
            command=self.start_monitoring
        )
        self.start_monitor_btn.pack(side="left", padx=(0, 10))
        
        self.stop_monitor_btn = tk.Button(
            left_section,
            text="停止监控",
            font=("Microsoft YaHei", 12, "normal"),
            fg="#e6e6e6",
            bg="#2a2a2a",
            relief="flat",
            width=15,
            state="disabled",
            command=self.stop_monitoring
        )
        self.stop_monitor_btn.pack(side="left", padx=(0, 10))
        
        self.monitor_status_label = tk.Label(
            left_section,
            text="状态: 未监控",
            font=("Microsoft YaHei", 11, "normal"),
            fg="#d6d6d6",
            bg="#181818"
        )
        self.monitor_status_label.pack(side="left", padx=(0, 30))
        
        # 右侧：日志路径配置
        right_section = tk.Frame(content_row, bg="#181818")
        right_section.pack(side="left", fill="x", expand=True)
        
        tk.Label(
            right_section,
            text="监控日志:",
            font=("Microsoft YaHei", 11, "normal"),
            fg="#d6d6d6",
            bg="#181818"
        ).pack(side="left", padx=(0, 8))
        
        self.home_log_path_entry = tk.Entry(
            right_section,
            font=("Microsoft YaHei", 10, "normal"),
            fg="#bfbfbf",
            bg="#232323",
            relief="flat",
            width=40
        )
        self.home_log_path_entry.insert(0, self.log_file_path)
        self.home_log_path_entry.pack(side="left", ipady=5)
        
        tk.Button(
            right_section,
            text="浏览",
            font=("Microsoft YaHei", 10, "normal"),
            fg="#e6e6e6",
            bg="#2a2a2a",
            relief="flat",
            width=8,
            command=self.browse_home_log_file
        ).pack(side="left", padx=8)
        
        tk.Button(
            right_section,
            text="应用",
            font=("Microsoft YaHei", 10, "normal"),
            fg="#e6e6e6",
            bg="#4a9eff",
            relief="flat",
            width=8,
            command=self.apply_log_path
        ).pack(side="left")
        
        # 内容区域
        content_container = tk.Frame(self.home_page, bg="#1e1e1e")
        content_container.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        # 左侧战斗列表
        self.create_battle_list(content_container)
        
        # 右侧战斗详情
        self.create_battle_detail(content_container)
    
    def create_battle_list(self, parent):
        """创建战斗列表"""
        left_frame = tk.Frame(parent, bg="#181818", bd=1, relief="solid", width=420)
        left_frame.pack_propagate(False)
        left_frame.pack(side="left", fill="y")
        
        # 标题
        title_frame = tk.Frame(left_frame, bg="#181818", height=64)
        title_frame.pack_propagate(False)
        title_frame.pack(fill="x")
        
        tk.Label(
            title_frame,
            text="战斗列表",
            font=("Microsoft YaHei", 14, "normal"),
            fg="#e6e6e6",
            bg="#181818"
        ).pack(anchor="w", padx=24, pady=(20, 0))
        
        # 滚动区域
        canvas_container = tk.Frame(left_frame, bg="#181818")
        canvas_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_container, bg="#181818", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        self.battle_list_frame = tk.Frame(canvas, bg="#181818")
        
        self.battle_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.battle_list_frame, anchor="nw", width=400)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=8)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件（只在鼠标悬停时生效）
        def _on_list_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_list_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    
    def create_battle_detail(self, parent):
        """创建战斗详情"""
        right_frame = tk.Frame(parent, bg="#151515", bd=1, relief="solid")
        right_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))
        
        # 头部
        header_frame = tk.Frame(right_frame, bg="#151515")
        header_frame.pack(fill="x", padx=24, pady=(24, 20))
        
        tk.Label(
            header_frame,
            text="战斗详情",
            font=("Microsoft YaHei", 14, "normal"),
            fg="#e6e6e6",
            bg="#151515"
        ).pack(side="left")
        
        # 数据类型按钮
        btn_frame = tk.Frame(header_frame, bg="#151515")
        btn_frame.pack(side="right")
        
        self.damage_btn = tk.Button(
            btn_frame,
            text="伤害",
            font=("Microsoft YaHei", 11, "normal"),
            fg="#e6e6e6",
            bg="#a960ff",
            relief="flat",
            width=8,
            command=lambda: self.switch_view("damage")
        )
        self.damage_btn.pack(side="left", padx=5)
        
        self.healing_btn = tk.Button(
            btn_frame,
            text="治疗",
            font=("Microsoft YaHei", 11, "normal"),
            fg="#e6e6e6",
            bg="#2a2a2a",
            relief="flat",
            width=8,
            command=lambda: self.switch_view("healing")
        )
        self.healing_btn.pack(side="left", padx=5)
        
        self.death_btn = tk.Button(
            btn_frame,
            text="死亡",
            font=("Microsoft YaHei", 11, "normal"),
            fg="#e6e6e6",
            bg="#2a2a2a",
            relief="flat",
            width=8,
            command=lambda: self.switch_view("death")
        )
        self.death_btn.pack(side="left", padx=5)
        
        # 详情显示区域（添加滚动支持）
        detail_container = tk.Frame(right_frame, bg="#151515")
        detail_container.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        
        # 创建 Canvas 和 Scrollbar
        self.detail_canvas = tk.Canvas(detail_container, bg="#151515", highlightthickness=0)
        detail_scrollbar = tk.Scrollbar(detail_container, orient="vertical", command=self.detail_canvas.yview)
        
        self.detail_display_frame = tk.Frame(self.detail_canvas, bg="#151515")
        
        self.detail_display_frame.bind(
            "<Configure>",
            lambda e: self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all"))
        )
        
        # 创建canvas窗口，并设置宽度
        self.detail_canvas_window = self.detail_canvas.create_window((0, 0), window=self.detail_display_frame, anchor="nw")
        self.detail_canvas.configure(yscrollcommand=detail_scrollbar.set)
        
        # 绑定画布大小变化，调整内容宽度
        def _configure_canvas_width(event):
            canvas_width = event.width
            self.detail_canvas.itemconfig(self.detail_canvas_window, width=canvas_width)
        
        self.detail_canvas.bind('<Configure>', _configure_canvas_width)
        
        self.detail_canvas.pack(side="left", fill="both", expand=True)
        detail_scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        def _on_detail_mousewheel(event):
            self.detail_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.detail_canvas.bind("<Enter>", lambda e: self.detail_canvas.bind_all("<MouseWheel>", _on_detail_mousewheel))
        self.detail_canvas.bind("<Leave>", lambda e: self.detail_canvas.unbind_all("<MouseWheel>"))
    
    def create_log_control_page(self):
        """创建日志控制页面"""
        self.log_control_page = tk.Frame(self.content_frame, bg="#1e1e1e")
        
        # 配置区域
        config_frame = tk.Frame(self.log_control_page, bg="#181818", bd=1, relief="solid")
        config_frame.pack(fill="x", padx=40, pady=40)
        
        tk.Label(
            config_frame,
            text="导入与导出",
            font=("Microsoft YaHei", 14, "normal"),
            fg="#e6e6e6",
            bg="#181818"
        ).pack(anchor="w", padx=24, pady=(24, 20))
        
        # 日志文件路径
        path_frame = tk.Frame(config_frame, bg="#181818")
        path_frame.pack(fill="x", padx=24, pady=10)
        
        tk.Label(
            path_frame,
            text="日志文件路径:",
            font=("Microsoft YaHei", 11, "normal"),
            fg="#d6d6d6",
            bg="#181818"
        ).pack(anchor="w")
        
        path_input_frame = tk.Frame(path_frame, bg="#181818")
        path_input_frame.pack(fill="x", pady=(10, 0))
        
        self.log_path_entry = tk.Entry(
            path_input_frame,
            font=("Microsoft YaHei", 10, "normal"),
            fg="#bfbfbf",
            bg="#232323",
            relief="flat",
            width=80
        )
        self.log_path_entry.insert(0, self.log_file_path)
        self.log_path_entry.pack(side="left", ipady=8)
        
        tk.Button(
            path_input_frame,
            text="浏览",
            font=("Microsoft YaHei", 10, "normal"),
            fg="#e6e6e6",
            bg="#2a2a2a",
            relief="flat",
            width=10,
            command=self.browse_log_file
        ).pack(side="left", padx=10)
        
        # 按钮
        btn_frame = tk.Frame(config_frame, bg="#181818")
        btn_frame.pack(fill="x", padx=24, pady=20)
        
        tk.Button(
            btn_frame,
            text="导入并分析日志文件",
            font=("Microsoft YaHei", 12, "normal"),
            fg="#e6e6e6",
            bg="#a960ff",
            relief="flat",
            width=20,
            command=self.analyze_log_file
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="导出数据.json",
            font=("Microsoft YaHei", 12, "normal"),
            fg="#e6e6e6",
            bg="#2a2a2a",
            relief="flat",
            width=15,
            command=self.export_current_data
        ).pack(side="left")
    
    def show_page(self, page_name):
        """显示页面"""
        # 隐藏所有页面
        self.home_page.pack_forget()
        self.log_control_page.pack_forget()
        
        # 显示选中页面
        if page_name == "home":
            self.home_page.pack(fill="both", expand=True)
        elif page_name == "log_control":
            self.log_control_page.pack(fill="both", expand=True, padx=40, pady=40)
        
        # 更新标签样式
        for tab_name, (frame, label) in self.tabs.items():
            if tab_name == page_name:
                frame.configure(bg="#a960ff")
                label.configure(bg="#a960ff")
            else:
                frame.configure(bg="#252525")
                label.configure(bg="#252525")
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.log_file_path = self.log_path_entry.get()
        
        if not os.path.exists(self.log_file_path):
            messagebox.showwarning("警告", "日志文件不存在！")
            return
        
        self.monitor = RealtimeMonitor(self.log_file_path, self.monitor_callback)
        self.monitor.start()
        self.is_monitoring = True
        
        self.start_monitor_btn.config(state="disabled")
        self.stop_monitor_btn.config(state="normal")
        self.monitor_status_label.config(text="状态: 监控中...")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            return
        
        if self.monitor:
            self.monitor.stop()
        
        self.is_monitoring = False
        self.start_monitor_btn.config(state="normal")
        self.stop_monitor_btn.config(state="disabled")
        self.monitor_status_label.config(text="状态: 未监控")
    
    def monitor_callback(self, event_type, data):
        """监控回调"""
        if event_type == 'fight_update':
            # 更新当前战斗详情
            self.root.after(0, lambda: self.display_current_fight(data))
            # 更新悬浮窗
            self.current_fight_data = data
            if self.overlay_window:
                self.root.after(0, lambda: self.overlay_window.update_fight_data(data))
        elif event_type == 'fight_end':
            # 战斗结束，添加到列表
            self.root.after(0, lambda: self.add_fight_to_list(data))
            # 保持当前战斗数据（显示最终数据快照）
            self.current_fight_data = data
            # 更新主页和悬浮窗为最终数据
            self.root.after(0, lambda: self.display_current_fight(data))
            if self.overlay_window:
                self.root.after(0, lambda: self.overlay_window.update_fight_data(data))
    
    def display_current_fight(self, fight_data):
        """显示当前战斗数据"""
        if not fight_data:
            return
        
        # 清空详情显示区域
        for widget in self.detail_display_frame.winfo_children():
            widget.destroy()
        
        # 显示战斗信息
        info_frame = tk.Frame(self.detail_display_frame, bg="#1a1a1a", height=60)
        info_frame.pack_propagate(False)
        info_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            info_frame,
            text=f"当前战斗 · {fight_data['zone']} · 进行中 ({fight_data['duration']}秒)",
            font=("Microsoft YaHei", 12, "normal"),
            fg="#d6d6d6",
            bg="#1a1a1a"
        ).pack(anchor="w", padx=20, pady=18)
        
        # 根据当前视图显示数据
        if self.current_view_type == "damage":
            self.display_damage_data(fight_data['damage_done'])
        elif self.current_view_type == "healing":
            self.display_healing_data(fight_data['healing_done'])
        elif self.current_view_type == "death":
            self.display_death_data(fight_data['death_events'])
    
    def _display_stats_data(self, data, headers, rate_key):
        """通用的统计数据显示方法"""
        # 表头
        header_frame = tk.Frame(self.detail_display_frame, bg="#272727", height=48)
        header_frame.pack_propagate(False)
        header_frame.pack(fill="x", pady=(0, 10))
        
        positions = [24, 280, 480, 720, 920]
        for header, pos in zip(headers, positions):
            tk.Label(
                header_frame,
                text=header,
                font=("Microsoft YaHei", 10, "normal"),
                fg="#bfbfbf",
                bg="#272727"
            ).place(x=pos, y=14)
        
        # 数据行
        for i, player in enumerate(data[:10]):
            player_frame = tk.Frame(
                self.detail_display_frame,
                bg="#232323" if i % 2 == 0 else "#1e1e1e",
                height=56
            )
            player_frame.pack_propagate(False)
            player_frame.pack(fill="x", pady=4)
            
            # 使用字典驱动显示
            values = [
                player["name"],
                player["type"],
                f"{player['total']:,}",
                f"{player['percent']:.1f}%",
                f"{player.get(rate_key, 0):,.2f}"
            ]
            
            for value, pos in zip(values, positions):
                tk.Label(
                    player_frame,
                    text=value,
                    font=("Microsoft YaHei", 11, "normal"),
                    fg="#d6d6d6",
                    bg=player_frame.cget("bg")
                ).place(x=pos, y=18)
    
    def display_damage_data(self, damage_data):
        """显示伤害数据"""
        self._display_stats_data(damage_data, ["玩家", "职业", "总伤害", "占比", "DPS"], "dps")
    
    def display_healing_data(self, healing_data):
        """显示治疗数据"""
        self._display_stats_data(healing_data, ["玩家", "职业", "总治疗", "占比", "HPS"], "hps")
    
    def display_death_data(self, death_events):
        """显示死亡数据"""
        if not death_events:
            tk.Label(
                self.detail_display_frame,
                text="暂无死亡事件",
                font=("Microsoft YaHei", 12, "normal"),
                fg="#808080",
                bg="#151515"
            ).pack(pady=50)
            return
        
        # 表头
        header_frame = tk.Frame(self.detail_display_frame, bg="#272727", height=48)
        header_frame.pack_propagate(False)
        header_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["玩家", "职业", "死亡时间", "死亡原因"]
        positions = [24, 280, 480, 720]
        
        for header, pos in zip(headers, positions):
            tk.Label(
                header_frame,
                text=header,
                font=("Microsoft YaHei", 10, "normal"),
                fg="#bfbfbf",
                bg="#272727"
            ).place(x=pos, y=14)
        
        # 数据行
        for i, death in enumerate(death_events):
            death_frame = tk.Frame(
                self.detail_display_frame,
                bg="#232323" if i % 2 == 0 else "#1e1e1e",
                height=56
            )
            death_frame.pack_propagate(False)
            death_frame.pack(fill="x", pady=4)
            
            tk.Label(
                death_frame,
                text=death["name"],
                font=("Microsoft YaHei", 11, "normal"),
                fg="#d6d6d6",
                bg=death_frame.cget("bg")
            ).place(x=24, y=18)
            
            tk.Label(
                death_frame,
                text=death.get("type", "Unknown"),
                font=("Microsoft YaHei", 11, "normal"),
                fg="#d6d6d6",
                bg=death_frame.cget("bg")
            ).place(x=280, y=18)
            
            # 死亡时间格式化为 mm:ss
            death_time_ms = death["deathTime"]
            death_minutes = int(death_time_ms / 60000)
            death_seconds = int((death_time_ms % 60000) / 1000)
            death_time_str = f"{death_minutes:02d}:{death_seconds:02d}"
            
            tk.Label(
                death_frame,
                text=death_time_str,
                font=("Microsoft YaHei", 11, "normal"),
                fg="#d6d6d6",
                bg=death_frame.cget("bg")
            ).place(x=480, y=18)
            
            ability_name = death.get("ability", {}).get("name", "未知")
            tk.Label(
                death_frame,
                text=ability_name,
                font=("Microsoft YaHei", 11, "normal"),
                fg="#d6d6d6",
                bg=death_frame.cget("bg")
            ).place(x=720, y=18)
    
    def switch_view(self, view_type):
        """切换数据视图"""
        self.current_view_type = view_type
        
        # 更新按钮样式
        self.damage_btn.config(bg="#a960ff" if view_type == "damage" else "#2a2a2a")
        self.healing_btn.config(bg="#a960ff" if view_type == "healing" else "#2a2a2a")
        self.death_btn.config(bg="#a960ff" if view_type == "death" else "#2a2a2a")
        
        # 刷新显示
        if self.selected_fight:
            self.display_fight_detail(self.selected_fight)
    
    def add_fight_to_list(self, fight_data):
        """添加战斗到列表（实时监控）"""
        if not fight_data:
            return
        
        # 从 monitor 获取 analyzer 中的完整数据
        if self.monitor and self.monitor.analyzer:
            reports = self.monitor.analyzer._generate_reports()
            
            # 处理每个report（副本）
            for report in reports:
                zone_title = report['data']['reportData']['report']['title']
                report_fights = report['data']['reportData']['report']['fights']
                
                # 检查是否已经存在该副本的report
                existing_report = None
                for r in self.all_reports:
                    if r['data']['reportData']['report']['title'] == zone_title:
                        existing_report = r
                        break
                
                if existing_report:
                    # 副本已存在，只添加新的战斗（避免重复）
                    existing_fights = existing_report['data']['reportData']['report']['fights']
                    existing_fight_ids = {f['id'] for f in existing_fights}
                    
                    # 添加新战斗
                    for fight in report_fights:
                        if fight['id'] not in existing_fight_ids:
                            existing_fights.append(fight)
                    
                    # 更新副本的结束时间
                    existing_report['data']['reportData']['report']['endTime'] = report['data']['reportData']['report']['endTime']
                else:
                    # 新副本，直接添加
                    # 标记为实时监控数据（没有source_file）
                    report['source_file'] = 'realtime_monitor'
                    self.all_reports.append(report)
            
            # 刷新战斗列表
            self.refresh_battle_list()
    
    def display_fight_detail(self, fight):
        """显示战斗详情"""
        self.selected_fight = fight
        
        # 清空详情显示区域
        for widget in self.detail_display_frame.winfo_children():
            widget.destroy()
        
        # 显示战斗信息
        info_frame = tk.Frame(self.detail_display_frame, bg="#1a1a1a", height=60)
        info_frame.pack_propagate(False)
        info_frame.pack(fill="x", pady=(0, 10))
        
        # 计算持续时间（分秒格式）
        duration_ms = fight['duration']
        duration_minutes = int(duration_ms / 60000)
        duration_seconds = int((duration_ms % 60000) / 1000)
        duration_str = f"{duration_minutes:02d}:{duration_seconds:02d}"
        
        # 获取实际开始时间
        start_time_str = "未知时间"
        try:
            # 查找当前 fight 所在的 report
            for report in self.all_reports:
                report_data = report['data']['reportData']['report']
                if fight in report_data['fights']:
                    # 获取副本开始时间
                    report_start_time_str = report_data.get('startTime', '')
                    if report_start_time_str:
                        # 解析副本开始时间
                        report_start_time = datetime.fromisoformat(report_start_time_str.replace('+08:00', ''))
                        # 加上战斗的相对开始时间（毫秒）
                        fight_start_time = report_start_time + timedelta(milliseconds=fight.get('startTime', 0))
                        # 格式化为 xxxx年xx月xx日 xx:xx
                        start_time_str = fight_start_time.strftime("%Y年%m月%d日 %H:%M")
                    break
        except Exception as e:
            print(f"解析开始时间失败: {e}")
        
        tk.Label(
            info_frame,
            text=f"{fight['name']} · 持续时间: {duration_str} · 开始时间: {start_time_str}",
            font=("Microsoft YaHei", 12, "normal"),
            fg="#d6d6d6",
            bg="#1a1a1a"
        ).pack(anchor="w", padx=20, pady=18)
        
        # 根据当前视图显示数据
        if self.current_view_type == "damage":
            self.display_damage_data(fight['damageDone'])
        elif self.current_view_type == "healing":
            self.display_healing_data(fight['healingDone'])
        elif self.current_view_type == "death":
            self.display_death_data(fight['deathEvents'])
    
    def open_overlay_window(self):
        """打开悬浮窗"""
        if self.overlay_window and self.overlay_window.window.winfo_exists():
            # 悬浮窗已存在，显示并置顶
            self.overlay_window.window.deiconify()
            self.overlay_window.window.lift()
            self.overlay_window.window.attributes('-topmost', True)
        else:
            # 创建新的悬浮窗，传递图标路径
            self.overlay_window = OverlayWindow(self.root, self.icon_path)
            # 如果有当前战斗数据，立即更新
            if self.current_fight_data:
                self.overlay_window.update_fight_data(self.current_fight_data)
    
    def _browse_file(self, entry_widget, title="选择ACT日志文件"):
        """通用文件浏览方法"""
        filename = filedialog.askopenfilename(
            title=title,
            filetypes=[("日志文件", "*.log"), ("所有文件", "*.*")]
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
    
    def browse_home_log_file(self):
        """主页浏览日志文件"""
        self._browse_file(self.home_log_path_entry)
    
    def browse_log_file(self):
        """浏览日志文件"""
        self._browse_file(self.log_path_entry)
    
    def apply_log_path(self):
        """应用日志路径"""
        new_path = self.home_log_path_entry.get()
        
        if not os.path.exists(new_path):
            messagebox.showerror("错误", "日志文件不存在！")
            return
        
        if self.is_monitoring:
            messagebox.showwarning("警告", "请先停止监控再修改路径！")
            return
        
        self.log_file_path = new_path
        self.log_path_entry.delete(0, tk.END)
        self.log_path_entry.insert(0, new_path)
        messagebox.showinfo("成功", "日志路径已更新！")
    
    def analyze_log_file(self):
        """分析日志文件"""
        import json
        import threading
        from tkinter import ttk
        
        log_file = self.log_path_entry.get()
        
        if not os.path.exists(log_file):
            messagebox.showerror("错误", "日志文件不存在！")
            return
        
        # 获取绝对路径（用于比较）
        abs_log_file = os.path.abspath(log_file)
        
        # 检查是否已经导入过
        if abs_log_file in self.imported_log_files:
            # 提供选择：是否重新导入
            result = messagebox.askyesno(
                "重复导入", 
                f"该日志文件已经导入过！\n\n文件: {os.path.basename(log_file)}\n\n是否重新导入？\n（重新导入会清除之前的数据并重新加载）",
                icon='warning'
            )
            
            if not result:
                return
            
            # 用户选择重新导入，从记录中移除
            self.imported_log_files.discard(abs_log_file)
            # 从 all_reports 中移除该文件的数据（根据文件路径标记）
            self.all_reports = [r for r in self.all_reports if r.get('source_file') != abs_log_file]
        
        # 创建进度条窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("分析进度")
        progress_window.geometry("400x150")
        progress_window.configure(bg="#1e1e1e")
        progress_window.resizable(False, False)
        
        # 设置图标
        if os.path.exists(self.icon_path):
            try:
                progress_window.iconphoto(True, tk.PhotoImage(file=self.icon_path))
            except:
                pass
        
        # 居中显示
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # 进度标签
        tk.Label(
            progress_window,
            text="正在分析日志文件...",
            font=("Microsoft YaHei", 12),
            fg="#e6e6e6",
            bg="#1e1e1e"
        ).pack(pady=20)
        
        # 进度条
        progress_bar = ttk.Progressbar(
            progress_window,
            length=350,
            mode='determinate'
        )
        progress_bar.pack(pady=10)
        
        # 进度文本
        progress_label = tk.Label(
            progress_window,
            text="0%",
            font=("Microsoft YaHei", 10),
            fg="#d6d6d6",
            bg="#1e1e1e"
        )
        progress_label.pack(pady=5)
        
        # 进度更新函数
        def update_progress(current, total):
            if total > 0:
                percentage = int((current / total) * 100)
                progress_bar['value'] = percentage
                progress_label.config(text=f"{percentage}% ({current:,} / {total:,} 行)")
                progress_window.update()
        
        # 分析完成后的处理
        def on_analysis_complete(reports, error=None):
            try:
                progress_window.destroy()
            except:
                pass  # 窗口可能已经被关闭
            
            if error:
                messagebox.showerror("错误", f"分析失败: {str(error)}")
                return
            
            # 为每个 report 添加来源文件标记
            for report in reports:
                report['source_file'] = abs_log_file
            
            # 添加到现有数据
            self.all_reports.extend(reports)
            
            # 记录已导入的文件
            self.imported_log_files.add(abs_log_file)
            
            # 刷新战斗列表
            self.refresh_battle_list()
            
            messagebox.showinfo("成功", f"分析完成！共发现 {len(reports)} 个副本")
        
        # 在后台线程中执行分析
        def run_analysis():
            try:
                analyzer = ACTLogAnalyzer()
                reports = analyzer.analyze_log_file(log_file, progress_callback=update_progress)
                self.root.after(0, lambda: on_analysis_complete(reports))
            except Exception as e:
                self.root.after(0, lambda: on_analysis_complete(None, error=e))
        
        analysis_thread = threading.Thread(target=run_analysis, daemon=True)
        analysis_thread.start()
    
    def export_current_data(self):
        """导出当前数据"""
        import json
        
        if not self.all_reports:
            messagebox.showwarning("警告", "没有可导出的数据！")
            return
        
        # 让用户选择保存目录
        output_dir = filedialog.askdirectory(
            title="选择导出目录",
            initialdir=os.path.expanduser("~")
        )
        
        if not output_dir:  # 用户取消选择
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            exported_files = []
            for i, report in enumerate(self.all_reports):
                zone_title = report['data']['reportData']['report']['title']
                safe_zone_name = "".join(c for c in zone_title if c.isalnum() or c in (' ', '-', '_')).strip()
                if not safe_zone_name:
                    safe_zone_name = f"zone_{i+1}"
                
                output_file = os.path.join(output_dir, f"export_{safe_zone_name}_{timestamp}.json")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=4)
                
                exported_files.append(os.path.basename(output_file))
            
            # 显示导出成功信息
            file_list = "\n".join(exported_files)
            messagebox.showinfo("成功", f"已导出 {len(exported_files)} 个文件到:\n{output_dir}\n\n文件列表:\n{file_list}")
        
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def toggle_zone_fights(self, zone_name, fights_container):
        """切换副本战斗列表的显示/隐藏"""
        is_expanded = self.zone_expanded.get(zone_name, True)
        
        if is_expanded:
            # 折叠：隐藏战斗列表
            fights_container.pack_forget()
            self.zone_expanded[zone_name] = False
        else:
            # 展开：显示战斗列表
            fights_container.pack(fill="x", padx=(20, 8), pady=0)
            self.zone_expanded[zone_name] = True
    
    def refresh_battle_list(self):
        """刷新战斗列表"""
        # 清空当前列表
        for widget in self.battle_list_frame.winfo_children():
            widget.destroy()
        
        # 清空组件引用
        self.zone_widgets = {}
        
        # 按副本名称和时间组织数据
        for report in self.all_reports:
            report_data = report['data']['reportData']['report']
            zone_name = report_data['title']
            
            # 获取或初始化该副本的展开状态（默认展开）
            if zone_name not in self.zone_expanded:
                self.zone_expanded[zone_name] = True
            
            is_expanded = self.zone_expanded[zone_name]
            
            # 创建副本标题（可展开）
            zone_header = tk.Frame(self.battle_list_frame, bg="#2a2a2a", height=50, cursor="hand2")
            zone_header.pack_propagate(False)
            zone_header.pack(fill="x", padx=8, pady=4)
            
            # 展开/折叠图标
            icon = "▼" if is_expanded else "▶"
            
            zone_label = tk.Label(
                zone_header,
                text=f"{icon} {zone_name}",
                font=("Microsoft YaHei", 11, "bold"),
                fg="#d6d6d6",
                bg="#2a2a2a",
                cursor="hand2"
            )
            zone_label.pack(anchor="w", padx=16, pady=12)
            
            # 创建战斗列表容器（立即pack到副本标题后面）
            fights_container = tk.Frame(self.battle_list_frame, bg="#181818")
            # 根据展开状态决定pack还是pack_forget
            if is_expanded:
                fights_container.pack(fill="x", padx=(20, 8), pady=0)
            else:
                # 不显示，但仍然需要创建以便后续展开
                pass
            
            # 保存组件引用
            self.zone_widgets[zone_name] = {
                'header': zone_header,
                'container': fights_container
            }
            
            # 创建战斗列表（子项）
            for fight in report_data['fights']:
                fight_frame = tk.Frame(
                    fights_container,
                    bg="#232323",
                    height=50,
                    cursor="hand2"
                )
                fight_frame.pack_propagate(False)
                fight_frame.pack(fill="x", pady=2)
                
                fight_label = tk.Label(
                    fight_frame,
                    text=f"  {fight['name']}",
                    font=("Microsoft YaHei", 10, "normal"),
                    fg="#bfbfbf",
                    bg="#232323"
                )
                fight_label.pack(anchor="w", padx=16, pady=14)
                
                # 绑定点击事件
                fight_frame.bind("<Button-1>", lambda e, f=fight: self.display_fight_detail(f))
                fight_label.bind("<Button-1>", lambda e, f=fight: self.display_fight_detail(f))
            
            # 绑定副本标题点击事件
            zone_header.bind("<Button-1>", lambda e, zn=zone_name, zl=zone_label: self._on_zone_click(zn, zl))
            zone_label.bind("<Button-1>", lambda e, zn=zone_name, zl=zone_label: self._on_zone_click(zn, zl))
    
    def _on_zone_click(self, zone_name, zone_label):
        """处理副本标题点击事件"""
        # 获取组件引用
        if zone_name not in self.zone_widgets:
            return
        
        zone_header = self.zone_widgets[zone_name]['header']
        fights_container = self.zone_widgets[zone_name]['container']
        
        # 切换展开状态
        is_expanded = self.zone_expanded.get(zone_name, True)
        
        if is_expanded:
            # 折叠
            fights_container.pack_forget()
            self.zone_expanded[zone_name] = False
            zone_label.config(text=f"▶ {zone_name}")
        else:
            # 展开：使用pack的after参数指定位置在标题之后
            fights_container.pack(after=zone_header, fill="x", padx=(20, 8), pady=0)
            self.zone_expanded[zone_name] = True
            zone_label.config(text=f"▼ {zone_name}")
