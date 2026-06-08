@echo off
chcp 65001 >nul
echo ========================================
echo GitLens 英文原版恢复工具
echo ========================================
echo.
echo [1/2] 恢复 package.json...
echo.
python "%~dp0translate.py" restore
echo.
echo [2/2] 恢复 JS 文件...
echo.
python "%~dp0translate_js.py" restore
echo.
echo ========================================
echo 已恢复英文原版！请重启 VS Code/Cursor。
echo ========================================
echo.
echo 按任意键退出...
pause >nul
