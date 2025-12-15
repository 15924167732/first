#!/usr/bin/env python3
"""
单元测试运行脚本
"""

import os
import sys
import subprocess

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """运行所有单元测试"""
    # 使用pytest运行所有测试
    try:
        # 运行pytest命令
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            os.path.join(os.path.dirname(__file__)),
            '-v',  # 详细输出
            '--tb=short'  # 简洁的回溯信息
        ], cwd=os.path.join(os.path.dirname(__file__), '..'))
        
        # 返回测试结果状态码
        return result.returncode
    except FileNotFoundError:
        print("错误: 未找到pytest。请确保已安装pytest:")
        print("pip install pytest")
        return 1
    except Exception as e:
        print(f"运行测试时发生错误: {e}")
        return 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)