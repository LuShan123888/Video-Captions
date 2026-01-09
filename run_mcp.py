#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站字幕 MCP 服务器启动脚本

确保所有编码设置正确后再启动服务器
"""

import os
import sys

# 在任何其他导入之前设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'zh_CN.UTF-8'
os.environ['LC_ALL'] = 'zh_CN.UTF-8'

# 确保stdout/stderr使用UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 导入并运行MCP服务器
if __name__ == "__main__":
    # 直接运行mcp_server的主入口
    from mcp_server import mcp
    mcp.run()
