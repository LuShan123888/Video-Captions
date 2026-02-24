"""
视频字幕抓取工具 - CLI Handler

处理 CLI 命令行输入，调用 Service 层完成字幕下载
"""

import argparse
import asyncio
import os
import sys

from service import get_service
from core.formatter import ResponseFormat
from core.logging import log_info, set_verbose_log


def print_result(result: dict) -> None:
    """格式化打印字幕结果"""
    if "error" in result:
        print(f"\n错误: {result.get('error', '未知错误')}")
        if "message" in result:
            print(f"详情: {result['message']}")
        if "suggestion" in result:
            print(f"提示: {result['suggestion']}")
        return

    video_title = result.get("video_title", "未知")
    print(f"{'='*60}")
    print(f"视频标题: {video_title}")
    print(f"{'='*60}\n")

    content = result.get("content")
    if content:
        print(content)

    subtitle_count = result.get("subtitle_count", 0)
    print(f"\n共 {subtitle_count} 条字幕")


def main() -> None:
    """CLI 入口点"""
    parser = argparse.ArgumentParser(
        description="视频字幕下载工具，支持 B站、YouTube 和本地文件",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("source", help="视频 URL 或本地文件路径")
    parser.add_argument(
        "--browser",
        choices=["auto", "chrome", "edge", "firefox", "brave"],
        default="auto",
        help="从浏览器读取 Cookie"
    )
    parser.add_argument(
        "--model",
        choices=["base", "small", "medium", "large"],
        default="large",
        help="Whisper 模型大小"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    parser.add_argument(
        "--format",
        choices=["text", "srt", "json"],
        default="text",
        help="输出格式"
    )
    parser.add_argument("--list", action="store_true", help="仅列出可用字幕")
    parser.add_argument("--info", action="store_true", help="仅显示视频信息")

    args = parser.parse_args()

    if args.verbose:
        set_verbose_log(True)
        log_info("详细日志模式已启用")

    service = get_service(args.source, args.browser)
    if not service:
        print(f"错误: 不支持的来源: {args.source}")
        print("支持的平台: B站、YouTube、本地音频/视频文件")
        sys.exit(1)

    print(f"[video-captions] 检测到平台: {service.name}", file=sys.stderr)

    format = ResponseFormat(args.format)

    # 本地文件模式
    if service.name == "local":
        file_title = os.path.splitext(os.path.basename(args.source))[0]
        print(f"{'='*60}")
        print(f"文件名称: {file_title}")
        print(f"字幕来源: Whisper ASR语音识别 (AI生成)")
        print(f"{'='*60}\n")

        result = asyncio.run(service.download_subtitle(
            args.source, format, model_size=args.model
        ))
        print_result(result)
        return

    # 下载字幕
    result = asyncio.run(service.download_subtitle(args.source, format, model_size=args.model))
    print_result(result)


if __name__ == "__main__":
    main()
