"""
核心分析模块单元测试
"""

import os
import sys
import tempfile
from datetime import datetime
from collections import defaultdict

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.analyzer import ACTLogAnalyzer
from tests.test_constants import TEST_LOG_LINES


def setup_test_analyzer():
    """测试前置条件"""
    analyzer = ACTLogAnalyzer()
    
    # 创建临时测试文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
    temp_file.write('\n'.join(TEST_LOG_LINES))
    temp_file.close()
    
    return analyzer, temp_file


def teardown_test_analyzer(temp_file):
    """测试后清理"""
    # 删除临时文件
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


def test_clean_ability_name():
    """测试技能名称清理功能"""
    analyzer, temp_file = setup_test_analyzer()
    
    try:
        # 测试特殊情况
        assert analyzer.clean_ability_name("", "844B") == "坠机"
        assert analyzer.clean_ability_name("_rsv_12345", "1234") == "aoe"
        assert analyzer.clean_ability_name("unk_abc", "5678") == "攻击"
        
        # 测试普通情况
        assert analyzer.clean_ability_name("火炎", "12F3") == "火炎"
    finally:
        teardown_test_analyzer(temp_file)


def test_parse_timestamp():
    """测试时间戳解析功能"""
    analyzer, temp_file = setup_test_analyzer()
    
    try:
        # 测试正常时间戳
        timestamp_str = "2025-12-09T10:30:00.0000000+08:00"
        result = analyzer.parse_timestamp(timestamp_str)
        assert isinstance(result, datetime)
        
        # 测试异常时间戳
        invalid_timestamp = "invalid-timestamp"
        result = analyzer.parse_timestamp(invalid_timestamp)
        assert isinstance(result, datetime)  # 应该返回当前时间
    finally:
        teardown_test_analyzer(temp_file)


def test_get_or_create_report():
    """测试获取或创建报告功能"""
    analyzer, temp_file = setup_test_analyzer()
    
    try:
        zone_name = "测试区域"
        
        # 第一次获取应该创建新报告
        report = analyzer.get_or_create_report(zone_name)
        assert zone_name in analyzer.reports
        assert report['fight_count'] == 0
        
        # 第二次获取应该返回同一份报告
        report2 = analyzer.get_or_create_report(zone_name)
        assert report is report2
    finally:
        teardown_test_analyzer(temp_file)


def test_parse_damage():
    """测试伤害值解析功能"""
    analyzer, temp_file = setup_test_analyzer()
    
    try:
        # 测试正常伤害值
        assert analyzer.parse_damage("1F4", "") == 500  # 0x1F4 = 500
        
        # 测试特殊格式伤害值
        assert analyzer.parse_damage("4001F4", "") == 0x1F400  # 特殊格式
        
        # 测试无效伤害值
        assert analyzer.parse_damage("", "") == 0
        assert analyzer.parse_damage("invalid", "") == 0
    finally:
        teardown_test_analyzer(temp_file)


def test_analyze_log_file():
    """测试日志文件分析功能"""
    analyzer, temp_file = setup_test_analyzer()
    
    try:
        # 使用测试数据进行分析
        results = analyzer.analyze_log_file(temp_file.name)
        
        # 验证返回结果类型
        assert isinstance(results, list)
        
        # 验证基本结构
        for result in results:
            assert 'data' in result
            assert 'reportData' in result['data']
            assert 'report' in result['data']['reportData']
    finally:
        teardown_test_analyzer(temp_file)