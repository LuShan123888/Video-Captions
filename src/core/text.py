"""
文本处理 - 文件名处理、繁简转换
"""

import re
from opencc import OpenCC


def make_safe_filename(filename: str) -> str:
    """移除或替换文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def convert_to_simplified(text: str) -> str:
    """将繁体中文转换为简体中文"""
    try:
        cc = OpenCC('t2s')
        return cc.convert(text)
    except (TypeError, ValueError, RuntimeError):
        return text
