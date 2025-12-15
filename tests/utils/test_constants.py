"""
常量工具模块单元测试
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.constants import JOB_NAMES, LOG_TYPE_ADD_ENTITY, LOG_TYPE_ABILITY, LOG_TYPE_DEATH, LOG_TYPE_COMBAT_STATUS, LOG_TYPE_ZONE_CHANGE


def test_job_names():
    """测试职业名称映射"""
    # 验证一些已知的职业ID
    assert JOB_NAMES[19] == "骑士"
    assert JOB_NAMES[21] == "战士"
    assert JOB_NAMES[24] == "白魔法师"
    assert JOB_NAMES[31] == "机工士"
    assert JOB_NAMES[34] == "武士"
    assert JOB_NAMES[35] == "赤魔法师"
    
    # 验证字典不为空
    assert len(JOB_NAMES) > 0


def test_log_types():
    """测试日志类型常量"""
    # 验证日志类型常量
    assert LOG_TYPE_ADD_ENTITY == '03'
    assert LOG_TYPE_DEATH == '25'
    assert LOG_TYPE_COMBAT_STATUS == '260'
    assert LOG_TYPE_ZONE_CHANGE == '265'
    
    # 验证ABILITY类型是一个列表
    assert isinstance(LOG_TYPE_ABILITY, list)
    assert '21' in LOG_TYPE_ABILITY
    assert '22' in LOG_TYPE_ABILITY