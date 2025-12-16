"""
FF14战斗分析器 - 完整发布脚本
这个脚本将完成从打包到创建发布版本的全过程
"""

import os
import sys
import shutil
import zipfile
import subprocess
from datetime import datetime

def clean_previous_builds():
    """清理之前的构建"""
    print("清理之前的构建...")
    
    # 删除之前的构建目录
    dirs_to_remove = ["dist", "build", "release", "releases"]
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"删除目录: {dir_name}")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 运行PyInstaller命令
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--icon", "Dragoon.png",
        "--name", "FF14BattleAnalyzer",
        "--add-data", "Dragoon.png;.",
        "--add-data", "config.json;.",
        "main.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("构建过程中出现错误:")
        print(result.stderr)
        return False
    
    print("可执行文件构建完成")
    return True

def create_release_structure():
    """创建发布目录结构"""
    print("创建发布目录结构...")
    
    # 创建基本目录结构
    os.makedirs("release/FF14BattleAnalyzer", exist_ok=True)
    os.makedirs("release/FF14BattleAnalyzer/ACT.DieMoe/FFXIVLogs", exist_ok=True)
    
    # 复制构建结果
    if os.path.exists("dist/FF14BattleAnalyzer"):
        for item in os.listdir("dist/FF14BattleAnalyzer"):
            source = os.path.join("dist/FF14BattleAnalyzer", item)
            destination = os.path.join("release/FF14BattleAnalyzer", item)
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
    
    # 创建README文件
    create_readme()
    
    # 创建CHANGELOG文件
    create_changelog()
    
    print("发布目录结构创建完成")

def create_readme():
    """创建README文件"""
    readme_content = """FF14战斗分析器
================

这是一个用于分析FF14战斗日志的工具。

## 功能特性
- 实时监控ACT日志文件
- 离线分析历史战斗数据
- 显示伤害、治疗和死亡统计
- 悬浮窗实时显示战斗数据
- 支持多个副本和战斗分析

## 使用方法
1. 确保ACT正在运行并生成日志文件
2. 解压所有文件到一个目录
3. 右键点击 FF14BattleAnalyzer.exe 选择"以管理员身份运行"
4. 程序会自动检测ACT日志文件并开始分析

## 系统要求
- Windows 7 或更高版本
- .NET Framework 4.0 或更高版本

## 注意事项
- 程序需要管理员权限运行
- 确保ACT正在运行并生成日志文件
- 如果程序无法找到日志文件，请手动在界面中设置日志路径

## 技术支持
如有问题，请联系开发者或查看GitHub仓库。
"""
    
    with open("release/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

def create_changelog():
    """创建CHANGELOG文件"""
    changelog_content = f"""版本更新日志
==============

v1.0.0 ({datetime.now().strftime('%Y-%m-%d')})
------------------
- 初始版本发布
- 实现基本的实时监控功能
- 实现离线分析功能
- 添加悬浮窗显示
- 添加配置管理
"""
    
    with open("release/CHANGELOG.txt", "w", encoding="utf-8") as f:
        f.write(changelog_content)

def create_final_release():
    """创建最终发布版本"""
    print("创建最终发布版本...")
    
    # 获取当前日期作为版本号
    version = datetime.now().strftime("%Y%m%d")
    release_name = f"FF14BattleAnalyzer_v{version}"
    release_dir = f"releases/{release_name}"
    
    # 创建发布目录
    os.makedirs(release_dir, exist_ok=True)
    
    # 复制发布文件
    if os.path.exists("release"):
        for item in os.listdir("release"):
            source = os.path.join("release", item)
            destination = os.path.join(release_dir, item)
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
    
    # 创建zip压缩包
    zip_filename = f"releases/{release_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, release_dir)
                # 确保使用UTF-8编码处理文件名
                zipf.write(file_path, f"{release_name}/{arc_path}")
    
    print("最终发布版本创建完成")
    return release_dir, zip_filename

def main():
    """主函数"""
    print("=== FF14战斗分析器发布脚本 ===")
    print()
    
    # 清理之前的构建
    clean_previous_builds()
    
    # 构建可执行文件
    if not build_executable():
        print("构建失败，退出发布流程")
        return
    
    # 创建发布结构
    create_release_structure()
    
    # 创建最终发布版本
    release_dir, zip_filename = create_final_release()
    
    print()
    print("=== 发布完成 ===")
    print(f"发布目录: {os.path.abspath(release_dir)}")
    print(f"Zip包: {os.path.abspath(zip_filename)}")
    print()
    print("你现在可以将zip包分发给用户使用了!")

if __name__ == "__main__":
    main()