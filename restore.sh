#!/bin/bash

echo "========================================"
echo "GitLens 英文原版恢复工具"
echo "========================================"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/2] 恢复 package.json..."
echo
python3 "$SCRIPT_DIR/translate.py" restore
echo

echo "[2/2] 恢复 JS 文件..."
echo
python3 "$SCRIPT_DIR/translate_js.py" restore
echo

echo "========================================"
echo "已恢复英文原版！请重启 VS Code/Cursor。"
echo "========================================"
echo
