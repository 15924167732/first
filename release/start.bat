@echo off
chcp 65001 >nul
echo FF14战斗分析器启动脚本
echo ========================
echo.

REM 检查程序文件是否存在
if not exist "FF14BattleAnalyzer.exe" (
    echo 错误: 找不到 FF14BattleAnalyzer.exe 文件
    echo 请确保所有文件都在同一目录下
    echo.
    pause
    exit /b 1
)

REM 以管理员权限启动程序
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 正在启动 FF14战斗分析器...
    echo.
    start "" "FF14BattleAnalyzer.exe"
) else (
    echo 请求管理员权限以启动 FF14战斗分析器...
    echo.
    powershell -Command "Start-Process -FilePath '.\FF14BattleAnalyzer.exe' -Verb RunAs"
)

echo 程序启动中，请稍候...
timeout /t 2 /nobreak >nul