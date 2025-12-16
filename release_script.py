"""
FF14战斗分析器 - 发布脚本
"""

import os
import sys
import shutil
import zipfile
from datetime import datetime

def create_release_folder():
    """创建发布文件夹"""
    # 获取当前日期作为版本号
    version = datetime.now().strftime("%Y%m%d")
    release_dir = f"releases/FF14BattleAnalyzer_v{version}"
    
    # 如果目录已存在，删除它
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    
    # 创建新目录
    os.makedirs(release_dir, exist_ok=True)
    return release_dir, version

def copy_necessary_files(release_dir):
    """复制必要的文件到发布目录"""
    # 复制主程序目录
    if os.path.exists("release/FF14BattleAnalyzer"):
        shutil.copytree("release/FF14BattleAnalyzer", f"{release_dir}/FF14BattleAnalyzer")
    
    # 创建README文件
    readme_content = """FF14战斗分析器
================

这是一个用于分析FF14战斗日志的工具。

使用方法：
1. 解压所有文件到一个目录
2. 运行 FF14BattleAnalyzer.exe
3. 程序会自动检测ACT日志文件并开始分析

系统要求：
- Windows 7 或更高版本
- .NET Framework 4.0 或更高版本

注意事项：
- 程序需要管理员权限运行
- 确保ACT正在运行并生成日志文件
"""
    
    with open(f"{release_dir}/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 复制许可证文件（如果存在）
    if os.path.exists("LICENSE"):
        shutil.copy("LICENSE", release_dir)

def create_zip_package(release_dir, version):
    """创建zip压缩包"""
    zip_filename = f"releases/FF14BattleAnalyzer_v{version}.zip"
    
    # 如果zip文件已存在，删除它
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
    
    # 创建zip文件
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, release_dir)
                zipf.write(file_path, f"FF14BattleAnalyzer_v{version}/{arc_path}")
    
    return zip_filename

def main():
    """主函数"""
    print("开始创建发布版本...")
    
    # 创建发布目录
    release_dir, version = create_release_folder()
    print(f"创建发布目录: {release_dir}")
    
    # 复制必要文件
    copy_necessary_files(release_dir)
    print("文件复制完成")
    
    # 创建zip压缩包
    zip_filename = create_zip_package(release_dir, version)
    print(f"创建zip包: {zip_filename}")
    
    print("发布版本创建完成!")
    print(f"版本: v{version}")
    print(f"发布目录: {os.path.abspath(release_dir)}")
    print(f"Zip包: {os.path.abspath(zip_filename)}")

if __name__ == "__main__":
    main()