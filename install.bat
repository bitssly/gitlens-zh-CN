@echo off
chcp 65001 >nul
echo ========================================
echo GitLens 中文翻译安装工具
echo ========================================
echo.

python "%~dp0translate.py" install

echo.
echo 按任意键退出...
pause >nul
