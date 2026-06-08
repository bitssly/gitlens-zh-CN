#!/bin/bash

echo "========================================"
echo "GitLens 中文翻译安装工具"
echo "========================================"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/translate.py" install

echo
echo "按 Enter 键退出..."
read
