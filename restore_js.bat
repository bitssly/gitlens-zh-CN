@echo off
chcp 65001 >nul
echo ========================================
echo GitLens JS 翻译恢复
echo ========================================
echo.
python "%~dp0translate_js.py" restore
echo.
echo 按任意键退出...
pause >nul
