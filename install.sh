#!/bin/bash
set -e

echo "========================================"
echo "GitLens 中文翻译安装工具"
echo "========================================"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/2] 安装 package.json 翻译..."
echo
python3 "$SCRIPT_DIR/translate.py" install
echo

echo "[2/2] 应用 JS 文件翻译..."
echo
python3 "$SCRIPT_DIR/translate_js.py" apply
echo

echo "========================================"
echo "翻译安装完成！请重启 VS Code/Cursor。"
echo "========================================"
echo
