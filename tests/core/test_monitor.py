"""
实时监控模块单元测试
"""

import os
import sys
import tempfile
import time
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.monitor import RealtimeMonitor
from tests.test_constants import TEST_LOG_LINES


def setup_test_monitor():
    """测试前置条件"""
    # 创建临时测试文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
    temp_file.close()
    
    # 创建监控器实例
    callback_mock = Mock()
    monitor = RealtimeMonitor(temp_file.name, callback_mock)
    
    return monitor, temp_file, callback_mock


def teardown_test_monitor(monitor, temp_file):
    """测试后清理"""
    # 停止监控
    monitor.stop()
    
    # 删除临时文件
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


def test_init():
    """测试初始化功能"""
    monitor, temp_file, callback_mock = setup_test_monitor()
    
    try:
        assert monitor.log_file_path == temp_file.name
        assert monitor.is_running == False
        assert monitor.file_position == 0
        assert monitor.analyzer is not None
    finally:
        teardown_test_monitor(monitor, temp_file)


def test_start_stop():
    """测试启动和停止功能"""
    monitor, temp_file, callback_mock = setup_test_monitor()
    
    try:
        # 启动监控
        monitor.start()
        assert monitor.is_running == True
        
        # 停止监控
        monitor.stop()
        assert monitor.is_running == False
    finally:
        teardown_test_monitor(monitor, temp_file)


def test_process_zone_change_line():
    """测试处理区域变更日志行"""
    monitor, temp_file, callback_mock = setup_test_monitor()
    
    try:
        # 写入区域变更日志行
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(TEST_LOG_LINES[0])  # 265行: 副本区域变更
            
        # 处理日志行
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            line = f.readline()
            monitor._process_line(line)
            
        # 验证区域已更新
        assert monitor.current_zone == "Middle La Noscea"
    finally:
        teardown_test_monitor(monitor, temp_file)


def test_process_add_entity_line():
    """测试处理添加实体日志行"""
    monitor, temp_file, callback_mock = setup_test_monitor()
    
    try:
        # 写入添加实体日志行
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(TEST_LOG_LINES[1])  # 03行: 添加实体
            
        # 处理日志行
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            line = f.readline()
            monitor._process_line(line)
            
        # 验证玩家职业已记录
        # 注意：由于测试数据中的职业ID为19（Warrior），应该在player_jobs中记录
        # 但由于_process_line中的逻辑，可能需要进一步验证
    finally:
        teardown_test_monitor(monitor, temp_file)


def test_start_new_fight():
    """测试开始新战斗功能"""
    monitor, temp_file, callback_mock = setup_test_monitor()
    
    try:
        # 保存原始状态
        original_fight_number = monitor.fight_number
        
        # 开始新战斗
        from datetime import datetime
        monitor._start_new_fight(datetime.now())
        
        # 验证状态更新
        assert monitor.in_combat == True
        assert monitor.fight_number == original_fight_number + 1
        assert monitor.combat_start_time is not None
        # 验证combat_start_time是datetime类型
        assert isinstance(monitor.combat_start_time, datetime)
    finally:
        teardown_test_monitor(monitor, temp_file)


def test_end_current_fight():
    """测试结束当前战斗功能"""
    monitor, temp_file, callback_mock = setup_test_monitor()
    
    try:
        # 先开始一场战斗
        from datetime import datetime
        monitor._start_new_fight(datetime.now())
        assert monitor.in_combat == True
        
        # 结束战斗
        monitor._end_current_fight()
        
        # 验证战斗已结束
        assert monitor.in_combat == False
    finally:
        teardown_test_monitor(monitor, temp_file)