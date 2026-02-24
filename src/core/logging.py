"""
日志系统 - 统一的日志输出
"""

import sys

# 设置环境变量确保 UTF-8 编码
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 确保 stdout/stderr 使用 UTF-8 编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

_verbose_log = False
_LOG_PREFIX = "[video-captions]"


def set_verbose_log(enabled: bool = True) -> None:
    """启用/禁用详细日志"""
    global _verbose_log
    _verbose_log = enabled


def log_info(message: str) -> None:
    """打印信息日志"""
    print(f"{_LOG_PREFIX} {message}", file=sys.stderr)


def log_step(step: str, message: str = "") -> None:
    """打印步骤日志"""
    if message:
        print(f"{_LOG_PREFIX} ▶ {step}: {message}", file=sys.stderr)
    else:
        print(f"{_LOG_PREFIX} ▶ {step}", file=sys.stderr)


def log_success(message: str) -> None:
    """打印成功日志"""
    print(f"{_LOG_PREFIX} ✓ {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    """打印警告日志"""
    print(f"{_LOG_PREFIX} ⚠ {message}", file=sys.stderr)


def log_error(message: str) -> None:
    """打印错误日志"""
    print(f"{_LOG_PREFIX} ✗ {message}", file=sys.stderr)


def log_debug(message: str) -> None:
    """打印调试日志（仅在详细模式下）"""
    if _verbose_log:
        print(f"{_LOG_PREFIX}   └─ {message}", file=sys.stderr)
