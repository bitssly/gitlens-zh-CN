@echo off
chcp 65001 >nul
echo ========================================
echo GitLens JS 文件翻译
echo ========================================
echo.
python "%~dp0translate_js.py" preview
echo.
echo 按任意键退出...
pause >nul
