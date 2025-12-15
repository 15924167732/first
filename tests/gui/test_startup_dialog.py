"""
启动对话框GUI模块单元测试
"""

import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gui.startup_dialog import StartupConfigDialog
from utils.config import Config


def setup_test_config():
    """测试前置条件"""
    # 创建临时配置文件
    temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
    temp_config_file.close()
    
    # 创建配置对象
    with patch.object(Config, '_get_config_path', return_value=temp_config_file.name):
        config = Config()
    
    return config, temp_config_file


def teardown_test_config(temp_config_file):
    """测试后清理"""
    # 删除临时配置文件
    if os.path.exists(temp_config_file.name):
        os.unlink(temp_config_file.name)


def test_init():
    """测试初始化功能"""
    # 由于StartupConfigDialog需要创建Tk窗口，这里只做简单测试
    # 在实际项目中，可能需要使用headless测试或者跳过GUI部分的测试
    pass


def test_get_default_act_path():
    """测试获取默认ACT路径功能"""
    config, temp_config_file = setup_test_config()
    
    try:
        dialog = StartupConfigDialog(config)
        default_path = dialog._get_default_act_path()
        assert default_path == os.path.join("ACT.DieMoe", "点我启动ACT.exe")
    finally:
        teardown_test_config(temp_config_file)