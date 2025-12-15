"""
FF14战斗分析器 - 配置管理
"""

import os
import json


class Config:
    """配置管理类"""
    
    def __init__(self):
        """初始化配置"""
        self.config_file = self._get_config_path()
        self.data = self._load_config()
    
    def _get_config_path(self):
        """获取配置文件路径"""
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, "config.json")
    
    def _load_config(self):
        """加载配置"""
        default_config = {
            "auto_start_act": True,  # 默认自动启动ACT
            "act_path": "",  # ACT启动文件路径，空表示使用默认路径
            "minimize_act": True  # 是否最小化ACT窗口
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置（保留默认值，覆盖已有的配置）
                    default_config.update(loaded_config)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.data.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.data[key] = value
    
    def get_auto_start_act(self):
        """获取是否自动启动ACT"""
        return self.data.get("auto_start_act", True)
    
    def set_auto_start_act(self, value):
        """设置是否自动启动ACT"""
        self.data["auto_start_act"] = value
    
    def get_act_path(self):
        """获取ACT启动文件路径"""
        return self.data.get("act_path", "")
    
    def set_act_path(self, path):
        """设置ACT启动文件路径"""
        self.data["act_path"] = path
    
    def get_minimize_act(self):
        """获取是否最小化ACT窗口"""
        return self.data.get("minimize_act", True)
    
    def set_minimize_act(self, value):
        """设置是否最小化ACT窗口"""
        self.data["minimize_act"] = value
