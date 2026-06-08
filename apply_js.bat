@echo off
chcp 65001 >nul
echo ========================================
echo GitLens JS 翻译应用
echo ========================================
echo.
python "%~dp0translate_js.py" apply
echo.
echo 按任意键退出...
pause >nul
