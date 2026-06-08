#!/bin/bash
# GitLens JS 文件翻译 - 恢复原版
echo "========================================"
echo "GitLens JS 翻译恢复"
echo "========================================"
echo
python3 "$(dirname "$0")/translate_js.py" restore
echo
