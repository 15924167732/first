# 单元测试说明

## 测试结构

本项目的单元测试按照模块划分，目录结构如下：

```
tests/
├── __init__.py
├── test_constants.py
├── run_tests.py
├── core/
│   ├── __init__.py
│   ├── test_analyzer.py
│   └── test_monitor.py
├── gui/
│   ├── __init__.py
│   └── test_startup_dialog.py
└── utils/
    ├── __init__.py
    ├── test_config.py
    └── test_constants.py
```

## 运行测试

### 运行所有测试

```bash
python tests/run_tests.py
```

### 运行特定模块的测试

```bash
# 运行核心模块测试
pytest tests/core/test_analyzer.py
pytest tests/core/test_monitor.py

# 运行GUI模块测试
pytest tests/gui/test_startup_dialog.py

# 运行工具模块测试
pytest tests/utils/test_config.py
pytest tests/utils/test_constants.py
```

### 运行带详细输出的测试

```bash
pytest tests/ -v
```

## 测试覆盖率

当前测试覆盖了以下主要功能：

1. **核心分析模块** (`core/analyzer.py`)
   - 日志解析功能
   - 伤害值计算
   - 时间戳处理
   - 报告生成

2. **实时监控模块** (`core/monitor.py`)
   - 日志文件监控
   - 战斗状态跟踪
   - 区域变更处理
   - 实体添加处理

3. **配置模块** (`utils/config.py`)
   - 配置文件读取和保存
   - 配置项访问和修改

4. **常量模块** (`utils/constants.py`)
   - 职业名称映射
   - 日志类型定义

5. **GUI模块** (`gui/startup_dialog.py`)
   - 启动对话框功能

## 编写新测试

1. 在相应的测试目录中创建新的测试文件，命名为 `test_*.py`
2. 编写测试函数，函数名以 `test_` 开头
3. 使用 `assert` 语句验证预期结果
4. 在 `tests/run_tests.py` 中添加必要的导入（如果需要）

## 注意事项

1. 测试使用临时文件和模拟对象，不会影响实际项目文件
2. GUI测试由于需要创建实际窗口，在某些环境中可能需要特殊配置
3. 测试数据存储在 `tests/test_constants.py` 中，可以根据需要扩展