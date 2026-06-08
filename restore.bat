@echo off
chcp 65001 >nul
echo ========================================
echo GitLens 英文原版恢复工具
echo ========================================
echo.

python "%~dp0translate.py" restore

echo.
echo 按任意键退出...
pause >nul
