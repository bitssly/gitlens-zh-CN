#!/usr/bin/env python3
"""
GitLens 中文翻译工具
支持 GitLens v18.x 的 package.json 汉化

用法:
    python translate.py install    # 安装翻译到 GitLens
    python translate.py restore    # 恢复英文原版
    python translate.py extract    # 提取未翻译的字符串
    python translate.py update     # 更新翻译数据
"""

import json
import sys
import os
import re
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# 配置
GITLENS_VERSION = "18.1.0"
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
OUTPUT_DIR = SCRIPT_DIR / "output"

# GitLens 扩展目录
def get_gitlens_dir():
    """获取 GitLens 扩展目录"""
    home = Path.home()
    extensions_dir = home / '.vscode' / 'extensions'

    # 查找 GitLens 目录
    for d in extensions_dir.iterdir():
        if d.name.startswith('eamodio.gitlens-'):
            return d

    return None

def load_json(filepath):
    """加载 JSON 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    """保存 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent='\t')

def contains_chinese(text):
    """检查字符串是否包含中文"""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[一-鿿]', text))

def is_translatable_key(key):
    """判断是否为需要翻译的 key"""
    translatable_keys = [
        'title', 'label', 'description', 'markdownDescription',
        'displayName', 'enumDescription', 'detail', 'markdownEnumDescriptions'
    ]
    return key in translatable_keys

def extract_translations(obj, path="", translations=None):
    """递归提取所有翻译映射"""
    if translations is None:
        translations = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, str) and contains_chinese(value):
                translations[current_path] = value
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    item_path = f"{current_path}[{i}]"
                    if isinstance(item, str) and contains_chinese(item):
                        translations[item_path] = item
                    elif isinstance(item, (dict, list)):
                        extract_translations(item, item_path, translations)
            elif isinstance(value, dict):
                extract_translations(value, current_path, translations)

    return translations

def apply_translations(obj, translations, path="", applied=None):
    """递归应用翻译到目标对象"""
    if applied is None:
        applied = set()

    if isinstance(obj, dict):
        for key in list(obj.keys()):
            current_path = f"{path}.{key}" if path else key
            value = obj[key]

            if isinstance(value, str) and current_path in translations:
                obj[key] = translations[current_path]
                applied.add(current_path)
            elif isinstance(value, list):
                for i in range(len(value)):
                    item_path = f"{current_path}[{i}]"
                    item = value[i]
                    if isinstance(item, str) and item_path in translations:
                        value[i] = translations[item_path]
                        applied.add(item_path)
                    elif isinstance(item, (dict, list)):
                        apply_translations(item, translations, item_path, applied)
            elif isinstance(value, dict):
                apply_translations(value, translations, current_path, applied)

    return applied

def count_strings(obj, count=0):
    """统计字符串数量"""
    if isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, str):
                count += 1
            elif isinstance(value, (dict, list)):
                count = count_strings(value, count)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, str):
                count += 1
            elif isinstance(item, (dict, list)):
                count = count_strings(item, count)
    return count

def count_chinese_strings(obj, count=0):
    """统计已翻译（含中文）的字符串数量"""
    if isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, str) and contains_chinese(value):
                count += 1
            elif isinstance(value, (dict, list)):
                count = count_chinese_strings(value, count)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, str) and contains_chinese(item):
                count += 1
            elif isinstance(item, (dict, list)):
                count = count_chinese_strings(item, count)
    return count

def extract_untranslated(obj, en_obj, path="", untranslated=None):
    """提取未翻译的字符串（英文原版有，翻译版没有的）"""
    if untranslated is None:
        untranslated = {}

    if isinstance(obj, dict) and isinstance(en_obj, dict):
        for key in obj:
            if key in en_obj:
                current_path = f"{path}.{key}" if path else key
                value = obj[key]
                en_value = en_obj[key]

                if isinstance(value, str) and isinstance(en_value, str):
                    if not contains_chinese(value) and en_value.strip():
                        untranslated[current_path] = en_value
                elif isinstance(value, (dict, list)) and isinstance(en_value, (dict, list)):
                    extract_untranslated(value, en_value, current_path, untranslated)

    elif isinstance(obj, list) and isinstance(en_obj, list):
        for i in range(min(len(obj), len(en_obj))):
            current_path = f"{path}[{i}]"
            item = obj[i]
            en_item = en_obj[i]

            if isinstance(item, str) and isinstance(en_item, str):
                if not contains_chinese(item) and en_item.strip():
                    untranslated[current_path] = en_item
            elif isinstance(item, (dict, list)) and isinstance(en_item, (dict, list)):
                extract_untranslated(item, en_item, current_path, untranslated)

    return untranslated

def cmd_install():
    """安装翻译到 GitLens"""
    gitlens_dir = get_gitlens_dir()
    if not gitlens_dir:
        print("错误: 找不到 GitLens 扩展目录")
        print("请确保已安装 GitLens 扩展")
        sys.exit(1)

    package_path = gitlens_dir / 'package.json'
    backup_path = gitlens_dir / 'package.json.backup'
    translated_path = DATA_DIR / 'package-v18-zh-partial.json'

    if not translated_path.exists():
        print(f"错误: 找不到翻译文件: {translated_path}")
        sys.exit(1)

    # 备份原文件
    if package_path.exists() and not backup_path.exists():
        print(f"备份原文件: {backup_path}")
        shutil.copy2(package_path, backup_path)

    # 安装翻译
    print(f"安装翻译到: {package_path}")
    shutil.copy2(translated_path, package_path)

    print("\n翻译安装完成!")
    print("请重启 VS Code 使翻译生效")
    print(f"\n如需恢复英文版，运行: python {__file__} restore")

def cmd_restore():
    """恢复英文原版"""
    gitlens_dir = get_gitlens_dir()
    if not gitlens_dir:
        print("错误: 找不到 GitLens 扩展目录")
        sys.exit(1)

    package_path = gitlens_dir / 'package.json'
    backup_path = gitlens_dir / 'package.json.backup'

    if not backup_path.exists():
        print(f"错误: 找不到备份文件: {backup_path}")
        print("无法恢复英文原版")
        sys.exit(1)

    print(f"恢复英文原版: {package_path}")
    shutil.copy2(backup_path, package_path)

    print("\n已恢复英文原版!")
    print("请重启 VS Code 生效")

def cmd_extract():
    """提取未翻译的字符串"""
    en_path = DATA_DIR / 'package-v18-en.json'
    zh_path = DATA_DIR / 'package-v18-zh-partial.json'

    if not en_path.exists():
        print(f"错误: 找不到英文原版: {en_path}")
        sys.exit(1)

    if not zh_path.exists():
        print(f"错误: 找不到翻译版: {zh_path}")
        sys.exit(1)

    print("加载文件...")
    en_data = load_json(en_path)
    zh_data = load_json(zh_path)

    print("提取未翻译字符串...")
    untranslated = extract_untranslated(zh_data, en_data)

    # 保存未翻译字符串
    output_path = OUTPUT_DIR / 'untranslated.json'
    save_json(output_path, untranslated)

    print(f"\n提取完成!")
    print(f"  未翻译字符串数: {len(untranslated)}")
    print(f"  已保存到: {output_path}")

    # 同时生成可读的文本版本
    txt_path = OUTPUT_DIR / 'untranslated.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"# GitLens v{GITLENS_VERSION} 未翻译字符串\n")
        f.write(f"# 提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 总数: {len(untranslated)}\n\n")

        for path, text in sorted(untranslated.items()):
            f.write(f"## {path}\n")
            f.write(f"{text}\n\n")

    print(f"  文本版已保存到: {txt_path}")

def cmd_update():
    """更新翻译数据（从当前已安装的翻译版提取）"""
    gitlens_dir = get_gitlens_dir()
    if not gitlens_dir:
        print("错误: 找不到 GitLens 扩展目录")
        sys.exit(1)

    package_path = gitlens_dir / 'package.json'
    if not package_path.exists():
        print(f"错误: 找不到 package.json: {package_path}")
        sys.exit(1)

    print("加载当前 package.json...")
    data = load_json(package_path)

    # 提取翻译
    print("提取翻译映射...")
    translations = extract_translations(data)

    # 保存翻译映射
    output_path = OUTPUT_DIR / 'translations.json'
    save_json(output_path, translations)

    print(f"\n提取完成!")
    print(f"  翻译映射数: {len(translations)}")
    print(f"  已保存到: {output_path}")

    # 同时更新 partial 文件
    partial_path = DATA_DIR / 'package-v18-zh-partial.json'
    shutil.copy2(package_path, partial_path)
    print(f"  已更新: {partial_path}")

def cmd_stats():
    """显示翻译统计信息"""
    en_path = DATA_DIR / 'package-v18-en.json'
    zh_path = DATA_DIR / 'package-v18-zh-partial.json'

    if not en_path.exists():
        print(f"错误: 找不到英文原版: {en_path}")
        sys.exit(1)

    if not zh_path.exists():
        print(f"错误: 找不到翻译版: {zh_path}")
        sys.exit(1)

    print("加载文件...")
    en_data = load_json(en_path)
    zh_data = load_json(zh_path)

    total = count_strings(en_data)
    translated = count_chinese_strings(zh_data)
    untranslated_count = total - translated

    print(f"\nGitLens v{GITLENS_VERSION} 翻译统计")
    print("=" * 40)
    print(f"  总字符串数:     {total}")
    print(f"  已翻译数:       {translated}")
    print(f"  未翻译数:       {untranslated_count}")
    print(f"  翻译覆盖率:     {translated/total*100:.1f}%")
    print("=" * 40)

def cmd_help():
    """显示帮助信息"""
    print(f"GitLens 中文翻译工具 v{GITLENS_VERSION}")
    print()
    print("用法:")
    print(f"  python {Path(__file__).name} install    安装翻译到 GitLens")
    print(f"  python {Path(__file__).name} restore    恢复英文原版")
    print(f"  python {Path(__file__).name} extract    提取未翻译的字符串")
    print(f"  python {Path(__file__).name} update     更新翻译数据")
    print(f"  python {Path(__file__).name} stats      显示翻译统计")
    print(f"  python {Path(__file__).name} help       显示此帮助")

def main():
    if len(sys.argv) < 2:
        cmd_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    commands = {
        'install': cmd_install,
        'restore': cmd_restore,
        'extract': cmd_extract,
        'update': cmd_update,
        'stats': cmd_stats,
        'help': cmd_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"未知命令: {command}")
        cmd_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
