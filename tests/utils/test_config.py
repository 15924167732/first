"""
配置工具模块单元测试
"""

import os
import sys
import tempfile
import json
from unittest.mock import patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.config import Config


def setup_test_config_file():
    """测试前置条件"""
    # 创建临时配置文件
    temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
    temp_config_file.close()
    
    return temp_config_file


def teardown_test_config_file(temp_config_file):
    """测试后清理"""
    # 删除临时配置文件
    if os.path.exists(temp_config_file.name):
        os.unlink(temp_config_file.name)


def test_init_with_no_config_file():
    """测试无配置文件时的初始化"""
    temp_config_file = setup_test_config_file()
    
    try:
        # 使用不存在的配置文件路径
        with patch.object(Config, '_get_config_path', return_value=temp_config_file.name):
            config = Config()
            
            # 验证默认配置
            assert config.get_auto_start_act() == True
            assert config.get_act_path() == ""
            assert config.get_minimize_act() == True
    finally:
        teardown_test_config_file(temp_config_file)


def test_init_with_existing_config_file():
    """测试有配置文件时的初始化"""
    temp_config_file = setup_test_config_file()
    
    try:
        # 创建配置文件内容
        config_data = {
            "auto_start_act": False,
            "act_path": "/custom/path/act.exe",
            "minimize_act": False
        }
        
        with open(temp_config_file.name, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
            
        # 使用存在的配置文件路径
        with patch.object(Config, '_get_config_path', return_value=temp_config_file.name):
            config = Config()
            
            # 验证加载的配置
            assert config.get_auto_start_act() == False
            assert config.get_act_path() == "/custom/path/act.exe"
            assert config.get_minimize_act() == False
    finally:
        teardown_test_config_file(temp_config_file)


def test_save_config():
    """测试保存配置功能"""
    temp_config_file = setup_test_config_file()
    
    try:
        with patch.object(Config, '_get_config_path', return_value=temp_config_file.name):
            config = Config()
            
            # 修改配置
            config.set_auto_start_act(False)
            config.set_act_path("/test/path/act.exe")
            config.set_minimize_act(False)
            
            # 保存配置
            config.save_config()
            
            # 验证文件已创建且内容正确
            assert os.path.exists(temp_config_file.name) == True
            
            with open(temp_config_file.name, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                
            assert saved_data["auto_start_act"] == False
            assert saved_data["act_path"] == "/test/path/act.exe"
            assert saved_data["minimize_act"] == False
    finally:
        teardown_test_config_file(temp_config_file)


def test_get_and_set_methods():
    """测试getter和setter方法"""
    temp_config_file = setup_test_config_file()
    
    try:
        with patch.object(Config, '_get_config_path', return_value=temp_config_file.name):
            config = Config()
            
            # 测试通用getter/setter
            config.set("test_key", "test_value")
            assert config.get("test_key") == "test_value"
            assert config.get("nonexistent_key", "default") == "default"
            
            # 测试专用getter/setter
            config.set_auto_start_act(False)
            assert config.get_auto_start_act() == False
            
            config.set_act_path("/another/path.exe")
            assert config.get_act_path() == "/another/path.exe"
            
            config.set_minimize_act(False)
            assert config.get_minimize_act() == False
    finally:
        teardown_test_config_file(temp_config_file)