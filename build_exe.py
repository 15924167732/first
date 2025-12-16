"""
FF14战斗分析器 - 打包脚本
"""

import os
import sys
import shutil

def create_distribution_folder():
    """创建发布文件夹"""
    dist_dir = "dist/FF14BattleAnalyzer"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)
    return dist_dir

def copy_assets(dist_dir):
    """复制资源文件"""
    # 复制图标文件
    if os.path.exists("Dragoon.png"):
        shutil.copy("Dragoon.png", dist_dir)
    
    # 复制默认配置
    if os.path.exists("config.json"):
        shutil.copy("config.json", dist_dir)
    
    # 创建ACT.DieMoe目录结构
    act_dir = os.path.join(dist_dir, "ACT.DieMoe")
    os.makedirs(act_dir, exist_ok=True)
    
    # 创建FFXIVLogs目录
    logs_dir = os.path.join(act_dir, "FFXIVLogs")
    os.makedirs(logs_dir, exist_ok=True)

def main():
    """主函数"""
    print("开始打包FF14战斗分析器...")
    
    # 创建发布文件夹
    dist_dir = create_distribution_folder()
    print(f"创建发布目录: {dist_dir}")
    
    # 复制资源文件
    copy_assets(dist_dir)
    print("资源文件复制完成")
    
    # 运行PyInstaller打包命令
    cmd = (
        "pyinstaller --noconfirm --onedir --windowed "
        "--icon Dragoon.png "
        "--name FF14BattleAnalyzer "
        "--add-data \"Dragoon.png;.\" "
        "--add-data \"config.json;.\" "
        "main.py"
    )
    
    print("正在运行打包命令...")
    print(cmd)
    result = os.system(cmd)
    
    if result != 0:
        print("打包过程中出现错误，请检查上面的输出信息。")
        return
    
    # 检查PyInstaller生成的目录是否存在
    built_dist = "dist/FF14BattleAnalyzer"
    source_dist = "dist/FF14BattleAnalyzer"
    
    # 如果source_dist不存在，尝试直接从dist目录复制
    if not os.path.exists(source_dist):
        source_dist = "dist"
    
    print(f"正在从 {source_dist} 复制文件到发布目录...")
    
    # 复制打包结果到发布目录
    if os.path.exists(source_dist):
        for item in os.listdir(source_dist):
            source = os.path.join(source_dist, item)
            destination = os.path.join(dist_dir, item)
            print(f"复制 {source} 到 {destination}")
            if os.path.isdir(source):
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
    
    print("打包完成!")
    print(f"发布文件位于: {os.path.abspath(dist_dir)}")

if __name__ == "__main__":
    main()