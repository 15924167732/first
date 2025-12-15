"""FF14战斗分析器 - 程序入口"""

import sys
import os
import tkinter as tk
import subprocess
import time
import threading
import atexit
import ctypes
from tkinter import messagebox


# 隐藏控制台窗口（仅Windows）
def hide_console():
    """隐藏控制台窗口"""
    try:
        # 获取控制台窗口句柄
        console_window = ctypes.windll.kernel32.GetConsoleWindow()
        if console_window:
            # 隐藏窗口 (SW_HIDE = 0)
            ctypes.windll.user32.ShowWindow(console_window, 0)
    except:
        pass

# 立即隐藏控制台
hide_console()


def is_admin():
    """检查当前是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def rerun_as_admin():
    """以管理员权限重新运行程序"""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas",  # 以管理员权限运行
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1  # SW_SHOWNORMAL
        )
        sys.exit(0)  # 退出当前实例
    except Exception as e:
        print(f"无法以管理员权限重启程序: {e}")
        sys.exit(1)


def check_single_instance():
    """检查是否已有程序实例在运行
    
    Returns:
        bool: True表示当前是唯一实例，False表示已有实例在运行
    """
    # 创建一个全局唯一的互斥锁名称
    mutex_name = "Global\\FF14BattleAnalyzer_SingleInstance_Mutex"
    
    # 尝试创建互斥锁
    try:
        # CreateMutexW: 创建或打开命名互斥锁
        # 参数: lpMutexAttributes, bInitialOwner, lpName
        mutex_handle = ctypes.windll.kernel32.CreateMutexW(
            None,  # 默认安全属性
            True,  # 当前进程拥有互斥锁
            mutex_name  # 互斥锁名称
        )
        
        # GetLastError: 获取最后的错误码
        # ERROR_ALREADY_EXISTS = 183 表示互斥锁已存在
        last_error = ctypes.windll.kernel32.GetLastError()
        
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            # 互斥锁已存在，说明程序已在运行
            if mutex_handle:
                ctypes.windll.kernel32.CloseHandle(mutex_handle)
            return False
        
        # 成功创建新互斥锁，当前是唯一实例
        # 注意：不要关闭mutex_handle，让它在程序运行期间一直保持
        return True
        
    except Exception as e:
        print(f"单实例检测失败: {e}")
        # 发生错误时允许运行
        return True


# 检查是否以管理员权限运行，如果不是则重新启动
if not is_admin():
    rerun_as_admin()

# 检查是否已有程序实例在运行
if not check_single_instance():
    # 创建临时的Tk窗口用于显示提示
    temp_root = tk.Tk()
    temp_root.withdraw()  # 隐藏主窗口
    temp_root.attributes('-alpha', 0.0)  # 完全透明
    temp_root.update_idletasks()  # 强制更新
    messagebox.showwarning(
        "程序已在运行",
        "FF14战斗分析器已经在运行中！\n\n请在系统托盘或任务栏中查找已运行的程序。",
        parent=temp_root
    )
    temp_root.quit()  # 先退出mainloop
    temp_root.destroy()  # 再销毁窗口
    sys.exit(0)

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入配置模块
from utils.config import Config
from gui.startup_dialog import StartupConfigDialog

# 导入重构后的模块
from gui.main_window import FF14BattleAnalyzer


def close_act():
    """关闭ACT程序"""
    try:
        # CREATE_NO_WINDOW = 0x08000000，隐藏子进程窗口
        CREATE_NO_WINDOW = 0x08000000
        
        # 直接终止ACT相关进程（不显示窗口）
        subprocess.run(['taskkill', '/F', '/IM', 'Advanced Combat Tracker.exe'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                      check=False, creationflags=CREATE_NO_WINDOW)
        subprocess.run(['taskkill', '/F', '/IM', 'ACT.DieMoe.Launcher.exe'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                      check=False, creationflags=CREATE_NO_WINDOW)
        subprocess.run(['taskkill', '/F', '/IM', '点我启动ACT.exe'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                      check=False, creationflags=CREATE_NO_WINDOW)
    except:
        pass


def minimize_act_window():
    """后台线程：等待ACT窗口加载完成后将其最小化"""
    try:
        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.windll.user32
        
        # 等待ACT进程启动
        time.sleep(5)
        
        # 定义回调函数类型
        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        
        # 查找ACT窗口并最小化
        def find_and_minimize(hwnd, lParam):
            try:
                if user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value.upper()
                        
                        # 匹配ACT主窗口（排除加载窗口）
                        if ("ADVANCED" in title and "COMBAT" in title) or "TRACKER" in title:
                            if "LOADING" not in title and "运行时" not in buff.value and "加载" not in buff.value:
                                user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
                                return False  # 找到后停止枚举
            except:
                pass
            return True
        
        # 持续监控30秒，每秒1秒检查一次
        for _ in range(30):
            callback = EnumWindowsProc(find_and_minimize)
            if not user32.EnumWindows(callback, 0):
                break  # 已找到并最小化
            time.sleep(1)
    except:
        pass


def start_act(act_path=None, minimize=True):
    """启动ACT程序
    
    Args:
        act_path: ACT启动文件路径，为None则使用默认路径
        minimize: 是否最小化ACT窗口
    """
    try:
        # 获取ACT程序路径
        if act_path and os.path.exists(act_path):
            # 使用用户指定的路径
            final_act_path = act_path
        else:
            # 使用默认路径（支持打包后的exe）
            if getattr(sys, 'frozen', False):
                # 打包后的exe，使用exe所在目录
                current_dir = os.path.dirname(sys.executable)
            else:
                # 开发环境，使用脚本目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
            final_act_path = os.path.join(current_dir, "ACT.DieMoe", "点我启动ACT.exe")
        
        if os.path.exists(final_act_path):
            # 以管理员权限启动ACT
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", final_act_path, None, 
                os.path.dirname(final_act_path), 1
            )
            
            # 如果需要最小化，启动后台线程监控并最小化ACT窗口
            if minimize:
                threading.Thread(target=minimize_act_window, daemon=True).start()
    except:
        pass


def main():
    """程序主入口"""
    # 加载配置
    config = Config()
    
    # 显示启动配置对话框
    startup_dialog = StartupConfigDialog(config)
    startup_dialog.show()  # 无论选择什么都继续
    
    # 注册退出时关闭ACT
    atexit.register(close_act)
    
    # 根据配置决定是否启动ACT
    if config.get_auto_start_act():
        act_path = config.get_act_path()
        minimize = config.get_minimize_act()
        start_act(act_path if act_path else None, minimize)
    
    # 启动分析器主界面
    root = tk.Tk()
    
    # 设置窗口图标
    try:
        # 支持打包后的exe
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(os.path.dirname(sys.executable), "Dragoon.png")
        else:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Dragoon.png")
        if os.path.exists(icon_path):
            root.iconphoto(True, tk.PhotoImage(file=icon_path))
    except:
        pass
    
    app = FF14BattleAnalyzer(root)
    
    # 绑定窗口关闭事件
    def on_closing():
        # 先解除所有绑定，防止重复触发
        root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        try:
            # 关闭悬浮窗
            if hasattr(app, 'overlay_window') and app.overlay_window:
                try:
                    app.overlay_window.window.withdraw()  # 先隐藏
                except:
                    pass
                try:
                    app.overlay_window.window.destroy()
                except:
                    pass
        except:
            pass
        
        try:
            # 停止监控
            if hasattr(app, 'monitor') and app.monitor:
                app.monitor.stop()
        except:
            pass
        
        try:
            # 隐藏主窗口
            root.withdraw()
        except:
            pass
        
        try:
            # 关闭ACT
            close_act()
        except:
            pass
        
        # 延迟销毁窗口，确保所有清理完成
        try:
            root.after(100, lambda: _final_cleanup())
        except:
            _final_cleanup()
    
    def _final_cleanup():
        """最终清理并退出"""
        try:
            root.destroy()
        except:
            pass
        # 强制退出
        os._exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
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


if __name__ == "__main__":
    main()
