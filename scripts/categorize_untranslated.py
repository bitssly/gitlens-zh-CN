#!/usr/bin/env python3
"""
将未翻译的 webview 字符串分类为：
- UI: 需要翻译的用户界面文本
- FRAMEWORK: 框架内部字符串，不需要翻译
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / 'output'

with open(OUTPUT_DIR / 'untranslated_webview.json', 'r', encoding='utf-8') as f:
    untranslated = json.load(f)

# 框架内部字符串模式 - 不需要翻译
FRAMEWORK_PATTERNS = [
    # DOM 事件
    'AnimationEnd', 'AnimationEvent', 'AnimationIteration', 'AnimationName', 'AnimationStart',
    'CustomEvent', 'DOMContentLoaded', 'CompositionEvent',
    'MSPointerDown', 'MSPointerMove', 'MSPointerUp',
    'TransitionCancel', 'TransitionEnd', 'TransitionEvent', 'TransitionRun', 'TransitionStart',
    'PointerEvent', 'ContextMenu',
    # React/框架内部
    'ForwardRef(', 'React.Children.only', 'ReactNative',
    'Ref-Current', 'Ref-Worktree', 'RefNodeAnnotationTarget',
    'DeprecatedPreview', 'DeprecatedPreviewExpired',
    'TrialExpired', 'TrialReactivationEligible', 'VerificationRequired',
    # CSS/样式
    'Webkit Moz O ms',
    # Graph 内部标识符
    'Graph-IsLoadingRows', 'Graph-NoCommits', 'Graph-WorkInProgress',
    'GraphApp.dispatch', 'GraphColumnMode', 'GraphHeader-', 'GraphMarkerShape',
    'GraphOverview:', 'GraphZone', 'OptionalGraphZone',
    'GL-AGENT-STATUS-PILL', 'GL-TREE-ITEM',
    'LeftPanelToGraphMarginGap', 'DndComponent',
    'RefZone-Enter', 'ScrollbarContainer', 'SortIndicator',
    'WipStatsPill', 'WorkDirMessageInput',
    'PatchDetailsApp', 'SettingsApp',
    # 内部错误/开发者消息
    'An error was suppressed during disposal',
    'Called getPending', 'Called hasSinks', 'Called hasSources',
    'Called introspectSinks', 'Called unwatch',
    'Cannot access private method', 'Cannot add the same',
    'Cannot call a class as a function', 'Cannot polyfill',
    'Class extends value ', 'Super expression must either',
    'The argument must be a React element',
    'Assertion error', 'AbortError', 'CancellationError',
    'NonCloneableError', 'ReferenceError', 'SuppressedError',
    'Invariant Violation', 'Infinite loop on byte',
    'Invalid color ctor', 'Invalid metadata', 'Invalid offset', 'Invalid size',
    'Detected cycle in computations', 'Detected cycle',
    'Color needs a value', 'CloseWatcher',
    'Unexpected private field',
    'Cannot call a class', 'Can only polyfill',
    'Property name required', 'Proxy target is not callable',
    'Target is not callable',
    'Stale proxy from previous session',
    'RemoteSignal is read-only',
    'Writes to signals not permitted',
    'Wrong receiver type for Signal',
    'SignalWatcherBrand', 'Symbol.asyncDispose', 'Symbol.dispose',
    'Value passed to', 'function must be a',
    'Unsupported decorator location',
    'JSON-tmLanguage', 'Nesting error',
    'Sortable: Cannot mount', 'Sortable: Mounted plugin',
    'Node is not an Element', 'The virtualize directive',
    'Requested index ', 'RPC connection aborted',
    'Failed to serialize resolved', 'Failed to subscribe', 'Failed to unsubscribe',
    'Proxy target is not callable',
    'VirtualFsError:', 'Lambda features disabled',
    'No compiler available',
    'Where is my file',
    'RowAdornmentInvalidateEvent',
    'ResizableHandleCorrection', 'ResizePanel',
    'CommitDateTimeSources',
    # 时间格式
    'MMM D, YYYY', 'MMMM Do, YYYY', 'MMMM Do, YYYY h:mma',
    'Timeline-NPlusYearsAgo',
    # 内部状态标识
    'ACTION-ITEM', 'GL-AGENT-STATUS-PILL', 'GL-TREE-ITEM',
    'PopoverBody', 'PopoverHeader', 'Popover Title', 'Popover description',
    'Carousel', 'Clear entry', 'Current value',
    'AnimationEnd', 'AnimationEvent',
    # 输入类型
    'INPUT', 'Alphanumeric',
    # 其他框架
    'Show More', 'Show Less', 'SHOW_MORE_COMMITS',
]

def is_framework(s):
    """判断字符串是否是框架内部的"""
    for pat in FRAMEWORK_PATTERNS:
        if pat in s:
            return True
    # 全大写+连字符的内部标识符
    if s.isupper() and '-' in s and len(s) > 5:
        return True
    # 以 . 开头或包含 ( 的错误消息
    if s.startswith('.') or (s.endswith('(') and len(s) < 30):
        return True
    return False

ui_strings = {}
framework_strings = {}

for s, files in untranslated.items():
    if is_framework(s):
        framework_strings[s] = files
    else:
        ui_strings[s] = files

print(f"总未翻译: {len(untranslated)}")
print(f"UI 字符串 (需翻译): {len(ui_strings)}")
print(f"框架内部 (跳过): {len(framework_strings)}")

# 保存 UI 字符串
with open(OUTPUT_DIR / 'ui_strings_to_translate.json', 'w', encoding='utf-8') as f:
    json.dump(ui_strings, f, ensure_ascii=False, indent='\t')

# 保存框架字符串
with open(OUTPUT_DIR / 'framework_strings_skipped.json', 'w', encoding='utf-8') as f:
    json.dump(framework_strings, f, ensure_ascii=False, indent='\t')

print(f"\nUI 字符串已保存到: {OUTPUT_DIR / 'ui_strings_to_translate.json'}")
print(f"框架字符串已保存到: {OUTPUT_DIR / 'framework_strings_skipped.json'}")

# 输出 UI 字符串列表
print(f"\n=== 需翻译的 UI 字符串 ({len(ui_strings)} 个) ===")
for s in sorted(ui_strings.keys()):
    print(f'  "{s}"')
