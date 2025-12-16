# FF14战斗分析器发布总结

## 发布版本信息
- **版本号**: v1.0.0
- **发布日期**: 2025年12月16日
- **文件大小**: 约26.7MB
- **文件名**: FF14BattleAnalyzer_v20251216.zip

## 发布内容

### 主要组件
1. **主程序**: FF14BattleAnalyzer.exe
2. **运行时依赖**: _internal目录下的所有文件
3. **资源配置**: Dragoon.png图标文件
4. **配置文件**: config.json
5. **启动脚本**: start.bat
6. **文档文件**: README.txt, CHANGELOG.txt, UserManual.md

### 功能特性
- 实时监控ACT日志文件
- 离线分析历史战斗数据
- 悬浮窗实时显示战斗数据
- 支持多个副本和战斗分析
- 简洁直观的用户界面

## 安装和使用说明

### 安装步骤
1. 下载发布包 `FF14BattleAnalyzer_v20251216.zip`
2. 解压缩到任意目录
3. 确保ACT正在运行并生成日志文件
4. 右键点击 `start.bat` 或 `FF14BattleAnalyzer.exe` 并选择"以管理员身份运行"

### 系统要求
- Windows 7 或更高版本
- .NET Framework 4.0 或更高版本
- 管理员权限运行

## 目录结构
```
FF14BattleAnalyzer_v20251216/
├── FF14BattleAnalyzer.exe     # 主程序
├── start.bat                 # 启动脚本
├── README.txt                # 使用说明
├── CHANGELOG.txt             # 版本更新日志
├── UserManual.md             # 用户手册
├── _internal/                # 程序运行依赖文件
│   ├── python312.dll         # Python运行时
│   ├── tkinter相关文件        # GUI库文件
│   └── 其他依赖文件...
├── ACT.DieMoe/              # ACT相关目录
│   └── FFXIVLogs/           # 日志文件目录
└── config.json              # 配置文件
```

## 技术实现细节

### 开发技术栈
- **编程语言**: Python 3.12
- **GUI框架**: Tkinter
- **打包工具**: PyInstaller
- **依赖管理**: pip

### 核心模块
1. **主程序模块** (`main.py`)
   - 程序入口点
   - 权限检查和单实例控制
   - 系统初始化

2. **用户界面层**
   - 主窗口模块 (`gui/main_window.py`)
   - 启动配置对话框 (`gui/startup_dialog.py`)
   - 悬浮窗模块 (`gui/overlay_window.py`)

3. **业务逻辑层**
   - 实时监控模块 (`core/monitor.py`)
   - 离线分析模块 (`core/analyzer.py`)
   - 配置管理模块 (`utils/config.py`)

4. **数据访问层**
   - 常量定义 (`utils/constants.py`)
   - 日志文件解析
   - 配置文件读写

### 打包流程
1. 使用PyInstaller将Python源代码编译为独立的exe文件
2. 自动包含所有依赖库和资源文件
3. 创建目录结构并复制必要文件
4. 生成zip压缩包便于分发

## 已知限制
1. 程序需要管理员权限运行
2. 依赖ACT生成的日志文件格式
3. 仅支持Windows平台
4. 大型日志文件分析可能需要较长时间

## 后续改进计划
1. 增加更多数据分析维度
2. 优化大型日志文件处理性能
3. 添加数据导出功能
4. 支持更多语言本地化
5. 增强错误处理和用户提示

## 技术支持
如有任何问题或建议，请通过以下方式联系我们：
- GitHub Issues
- 邮箱支持
- 社区论坛

---
**注意**: 本软件仅供个人使用，请遵守游戏服务条款和相关政策。