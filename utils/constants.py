"""
FF14战斗分析器 - 常量定义
"""

import os
import sys
import glob
from datetime import datetime

# 职业ID到名称的映射
JOB_NAMES = {
    1: "剑术师", 2: "格斗家", 3: "斧术师", 4: "枪术士",
    5: "弓箭手", 6: "幻术师", 7: "咒术师", 8: "刻木匠",
    9: "锻铁匠", 10: "铸甲匠", 11: "雕金师", 12: "制革匠",
    13: "裁衣匠", 14: "炼金师", 15: "烹饪师", 16: "采矿工",
    17: "园艺工", 18: "捕鱼人", 19: "骑士", 20: "武僧",
    21: "战士", 22: "龙骑士", 23: "诗人", 24: "白魔法师",
    25: "黑魔法师", 26: "秘术师", 27: "召唤师", 28: "学者",
    29: "双剑师", 30: "忍者", 31: "机工士", 32: "暗黑骑士",
    33: "占星术士", 34: "武士", 35: "赤魔法师", 36: "青魔法师",
    37: "绝枪战士", 38: "舞者", 39: "钐镰客", 40: "贤者",
    41: "蝰蛇", 42: "绘灵法师"
}

# 日志类型常量
LOG_TYPE_ADD_ENTITY = '03'
LOG_TYPE_ABILITY = ['21', '22']
LOG_TYPE_DEATH = '25'
LOG_TYPE_COMBAT_STATUS = '260'
LOG_TYPE_ZONE_CHANGE = '265'

# 默认配置
def get_default_log_path():
    """获取默认日志文件路径，自动查找当前日期的日志文件"""
    try:
        # 获取程序运行目录（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            # 打包后的exe，使用exe所在目录
            current_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境，使用脚本目录
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 构建FFXIVLogs目录的相对路径
        logs_dir = os.path.join(current_dir, "ACT.DieMoe", "FFXIVLogs")
        
        if not os.path.exists(logs_dir):
            # 如果目录不存在，返回默认值
            return r"D:\demo\Network_27406_20251209.log"
        
        # 获取当前日期（格式：YYYYMMDD）
        today = datetime.now().strftime("%Y%m%d")
        
        # 查找匹配当前日期的日志文件
        pattern = os.path.join(logs_dir, f"Network_*_{today}.log")
        matching_files = glob.glob(pattern)
        
        if matching_files:
            # 如果找到匹配的文件，返回第一个
            return matching_files[0]
        
        # 如果没有找到当前日期的文件，查找最新的日志文件
        all_logs = glob.glob(os.path.join(logs_dir, "Network_*.log"))
        if all_logs:
            # 按修改时间排序，返回最新的文件
            latest_log = max(all_logs, key=os.path.getmtime)
            return latest_log
        
        # 如果没有任何日志文件，返回默认路径
        return os.path.join(logs_dir, f"Network_27406_{today}.log")
    except:
        # 发生任何错误，返回默认值
        return r"D:\demo\Network_27406_20251209.log"

DEFAULT_LOG_PATH = get_default_log_path()
DEFAULT_OUTPUT_DIR = r"d:/demo"

# UI配置
WINDOW_GEOMETRY = "1920x1080"
OVERLAY_GEOMETRY = "300x200+100+100"
