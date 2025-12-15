"""
FF14战斗分析器 - 悬浮窗
"""

import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.constants import OVERLAY_GEOMETRY


class OverlayWindow:
    """悬浮窗类"""
    
    def __init__(self, parent, icon_path=None):
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.title("FF14战斗悬浮窗")
        self.window.attributes('-alpha', 0.55)
        # 设置窗口属性
        self.window.attributes('-topmost', True)
        self.window.geometry(OVERLAY_GEOMETRY)
        self.window.configure(bg="#1a1a1a")
        self.window.resizable(False, False)  # 禁止调整窗口大小
        self.enable_drag()

        # 设置窗口图标
        if icon_path and os.path.exists(icon_path):
            try:
                self.window.iconphoto(True, tk.PhotoImage(file=icon_path))
            except:
                pass
        
        # 创建界面
        self.setup_ui()
        
        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.hide_window)
    
    def hide_window(self):
        """隐藏窗口而不是销毁"""
        self.window.withdraw()
    
    def close(self):
        """关闭并销毁窗口"""
        try:
            self.window.destroy()
        except:
            pass
    
    def setup_ui(self):
        """设置界面"""
        # 数据区域（带滚动条）
        data_container = tk.Frame(self.window, bg="#1a1a1a")
        data_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(data_container, bg="#1a1a1a", highlightthickness=0)
        scrollbar = tk.Scrollbar(data_container, orient="vertical", command=canvas.yview)
        self.data_frame = tk.Frame(canvas, bg="#1a1a1a")
        
        self.data_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.data_frame, anchor="nw", width=280)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # 初始显示无战斗信息
        self.show_no_fight()
    def enable_drag(self):
        def start_move(event):
            self._x = event.x
            self._y = event.y

        def on_move(event):
            x = event.x_root - self._x
            y = event.y_root - self._y
            self.window.geometry(f"+{x}+{y}")

        self.window.bind("<Button-1>", start_move)
        self.window.bind("<B1-Motion>", on_move)

    def show_no_fight(self):
        """显示无战斗状态"""
        # 更新窗口标题
        self.window.title("FF14战斗悬浮窗 - 当前无战斗")
        
        # 清空数据区域
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        # 显示提示（固定字体大小）
        tk.Label(
            self.data_frame,
            text="当前无战斗",
            font=("Microsoft YaHei", 10, "normal"),
            fg="#808080",
            bg="#1a1a1a"
        ).pack(pady=80)
    
    def update_fight_data(self, fight_data):
        """更新战斗数据"""
        if not fight_data:
            self.show_no_fight()
            return
        
        # 更新窗口标题（显示副本信息）
        zone_name = fight_data.get('zone', '未知副本')
        duration = fight_data.get('duration', 0)
        
        # 格式化持续时间
        duration_minutes = int(duration / 60)
        duration_seconds = int(duration % 60)
        duration_str = f"{duration_minutes:02d}:{duration_seconds:02d}"
        
        # 设置窗口标题
        self.window.title(f"{zone_name} - {duration_str}")
        
        # 清空数据区域
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        # 获取玩家数据
        player_damage = fight_data.get('player_damage', {})
        player_healing = fight_data.get('player_healing', {})
        player_deaths = fight_data.get('player_deaths', {})
        player_info = fight_data.get('player_info', {})
        
        if duration > 0:
            # 表头（固定高度）
            header_frame = tk.Frame(self.data_frame, bg="#252525", height=22)
            header_frame.pack_propagate(False)
            header_frame.pack(fill="x", pady=(2, 2))
            
            # 调整表头：玩家、DPS、HPS、死亡（固定字体）
            tk.Label(
                header_frame,
                text="玩家",
                font=("Microsoft YaHei", 8, "bold"),
                fg="#bfbfbf",
                bg="#252525",
                width=10,
                anchor="w"
            ).pack(side="left", padx=2)
            
            tk.Label(
                header_frame,
                text="DPS",
                font=("Microsoft YaHei", 8, "bold"),
                fg="#bfbfbf",
                bg="#252525",
                width=8,
                anchor="e"
            ).pack(side="left", padx=2)
            
            tk.Label(
                header_frame,
                text="HPS",
                font=("Microsoft YaHei", 8, "bold"),
                fg="#bfbfbf",
                bg="#252525",
                width=8,
                anchor="e"
            ).pack(side="left", padx=2)
            
            tk.Label(
                header_frame,
                text="死亡",
                font=("Microsoft YaHei", 8, "bold"),
                fg="#bfbfbf",
                bg="#252525",
                width=4,
                anchor="center"
            ).pack(side="left", padx=2)
            
            # 收集所有玩家
            all_players = set()
            all_players.update(player_damage.keys())
            all_players.update(player_healing.keys())
            all_players.update(player_deaths.keys())
            
            # 按伤害排序
            players_list = []
            for player_id in all_players:
                damage = player_damage.get(player_id, 0)
                players_list.append((player_id, damage))
            
            players_list.sort(key=lambda x: x[1], reverse=True)
            
            # 显示玩家数据（最多8个）
            for i, (player_id, _) in enumerate(players_list[:8]):
                player_name = player_info.get(player_id, f"Unknown_{player_id}")
                damage = player_damage.get(player_id, 0)
                healing = player_healing.get(player_id, 0)
                deaths = player_deaths.get(player_id, 0)
                
                # 计算DPS和HPS
                dps = round(damage / duration, 1) if duration > 0 else 0
                hps = round(healing / duration, 1) if duration > 0 else 0
                
                # 玩家行（固定高度）
                player_frame = tk.Frame(
                    self.data_frame,
                    bg="#1e1e1e" if i % 2 == 0 else "#232323",
                    height=20
                )
                player_frame.pack_propagate(False)
                player_frame.pack(fill="x", pady=1)
                
                # 玩家名（截断长度）
                display_name = player_name[:8] if len(player_name) > 8 else player_name
                tk.Label(
                    player_frame,
                    text=display_name,
                    font=("Microsoft YaHei", 8, "normal"),
                    fg="#d6d6d6",
                    bg=player_frame.cget("bg"),
                    width=10,
                    anchor="w"
                ).pack(side="left", padx=2)
                
                # DPS
                tk.Label(
                    player_frame,
                    text=f"{dps:,.0f}",
                    font=("Microsoft YaHei", 8, "normal"),
                    fg="#ff6b6b",
                    bg=player_frame.cget("bg"),
                    width=8,
                    anchor="e"
                ).pack(side="left", padx=2)
                
                # HPS
                tk.Label(
                    player_frame,
                    text=f"{hps:,.0f}",
                    font=("Microsoft YaHei", 8, "normal"),
                    fg="#51cf66",
                    bg=player_frame.cget("bg"),
                    width=8,
                    anchor="e"
                ).pack(side="left", padx=2)
                
                # 死亡次数
                death_color = "#ff4444" if deaths > 0 else "#808080"
                tk.Label(
                    player_frame,
                    text=str(deaths),
                    font=("Microsoft YaHei", 8, "bold" if deaths > 0 else "normal"),
                    fg=death_color,
                    bg=player_frame.cget("bg"),
                    width=4,
                    anchor="center"
                ).pack(side="left", padx=2)
