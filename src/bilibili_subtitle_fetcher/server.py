#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站字幕 MCP 服务器

提供获取B站视频信息和字幕的工具。
"""

from typing import Literal
from mcp.server.fastmcp import FastMCP
from .api import (
    get_video_info,
    list_subtitles,
    download_subtitles_with_asr,
    ResponseFormat,
    make_safe_filename,
    get_sessdata,
)

# 初始化MCP服务器
mcp = FastMCP("bilibili_mcp")


# ============================================================================
# 工具定义
# ============================================================================


@mcp.tool()
async def bilibili_get_video_info(url: str) -> dict:
    """获取B站视频的基本信息，包括标题、时长、UP主等。

    Args:
        url: B站视频URL，例如: https://www.bilibili.com/video/BV1xx411c7mD/ 或 BV1xx411c7mD

    Returns:
        包含视频信息的字典:
        {
            "title": str,        # 视频标题
            "bvid": str,         # BV号
            "cid": int,          # 分P ID
            "duration": int,     # 视频时长（秒）
            "description": str,  # 视频简介
            "owner": {
                "name": str,     # UP主名称
                "mid": int       # UP主ID
            },
            "has_subtitle": bool # 是否有字幕
        }
    """
    try:
        return await get_video_info(url)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"获取视频信息时发生错误: {type(e).__name__}", "message": str(e)}


@mcp.tool()
async def bilibili_list_subtitles(url: str) -> dict:
    """列出视频可用的字幕语言和类型。

    Args:
        url: B站视频URL

    Returns:
        {
            "available": bool,      # 是否有可用字幕
            "subtitles": [
                {
                    "lan": str,          # 语言代码 (如 "ai-zh")
                    "lan_doc": str,      # 语言描述 (如 "中文（AI生成）")
                    "subtitle_url": str  # 字幕下载地址
                }
            ],
            "subtitle_count": int   # 字幕数量
        }

    Note:
        需要在 MCP 配置中设置 BILIBILI_SESSDATA 环境变量以获取 AI 字幕
    """
    try:
        sessdata = get_sessdata()
        return await list_subtitles(url, sessdata)
    except Exception as e:
        return {
            "available": False,
            "subtitles": [],
            "subtitle_count": 0,
            "error": str(e)
        }


@mcp.tool()
async def bilibili_download_subtitles(
    url: str,
    format: Literal["text", "srt", "json"] = "text",
    model_size: Literal["base", "small", "medium", "large"] = "medium"
) -> dict:
    """下载B站视频字幕内容，支持多种格式。

    优先从B站API获取字幕，若无字幕则使用Whisper ASR自动生成。

    Args:
        url: B站视频URL
        format: 输出格式
            - "text": 纯文本，适合阅读和总结
            - "srt": SRT字幕格式，适合视频播放
            - "json": 结构化JSON数据，适合程序处理
        model_size: ASR模型大小（当API无字幕时使用）
            - "base": 最快，精度较低
            - "small": 较快
            - "medium": 平衡（默认）
            - "large": 最慢，精度最高

    Returns:
        API字幕:
        {
            "source": "bilibili_api",
            "format": str,
            "subtitle_count": int,
            "content": str,          # text/srt格式
            "video_title": str
        }

        ASR字幕 (API无字幕时):
        {
            "source": "whisper_asr",
            "format": str,
            "subtitle_count": int,
            "content": str,
            "video_title": str
        }

        错误:
        {
            "error": str,
            "message": str
        }

    Note:
        - 需要在 MCP 配置中设置 BILIBILI_SESSDATA 环境变量以获取 AI 字幕
        - ASR 兜底需要安装 yt-dlp 和 ffmpeg
        - ASR 处理可能需要几分钟，请在 Claude Desktop 中增加超时时间
    """
    try:
        sessdata = get_sessdata()
        return await download_subtitles_with_asr(url, ResponseFormat(format), model_size, sessdata)
    except Exception as e:
        return {
            "error": f"下载字幕时发生错误: {type(e).__name__}",
            "message": str(e)
        }


# ============================================================================
# 主入口
# ============================================================================

def main() -> None:
    """MCP服务器入口点"""
    mcp.run()


if __name__ == "__main__":
    main()
