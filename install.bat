@echo off
chcp 65001 >nul
echo ========================================
echo GitLens 中文翻译安装工具
echo ========================================
echo.
echo [1/2] 安装 package.json 翻译...
echo.
python "%~dp0translate.py" install
echo.
echo [2/2] 应用 JS 文件翻译...
echo.
python "%~dp0translate_js.py" apply
echo.
echo ========================================
echo 翻译安装完成！请重启 VS Code/Cursor。
echo ========================================
echo.
echo 按任意键退出...
pause >nul
