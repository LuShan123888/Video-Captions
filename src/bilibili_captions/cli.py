# /// script
# dependencies = ["httpx", "mlx-whisper", "opencc-python-reimplemented"]
# -*-

"""
B站字幕抓取工具 - CLI 版本

支持从B站视频下载字幕，若无字幕则使用 Whisper ASR 生成。
"""

import asyncio
import os
import sys

from .core import (
    download_subtitles_with_asr,
    transcribe_file_with_asr,
    get_video_info,
    require_sessdata,
    ResponseFormat,
    get_sessdata_with_source,
)


def print_result(result: dict) -> None:
    """格式化打印字幕结果"""
    if "error" in result:
        print(f"\n错误: {result.get('error', '未知错误')}")
        if "message" in result:
            print(f"详情: {result['message']}")
        if "suggestion" in result:
            print(f"提示: {result['suggestion']}")
        return None

    source = result.get("source", "")

    # 打印视频标题框（ASR 模式已在 core.py 中打印，这里只处理 API 模式）
    if source != "whisper_asr":
        video_title = result.get("video_title", "未知")
        print(f"{'='*60}")
        print(f"视频标题: {video_title}")
        print(f"{'='*60}\n")

        # 打印字幕内容
        content = result.get("content")
        if content:
            print(content)

    subtitle_count = result.get("subtitle_count", 0)
    print(f"\n共 {subtitle_count} 条字幕")
    return None


def main() -> None:
    """CLI入口点"""
    if len(sys.argv) < 2:
        print("用法: bilibili-captions <B站视频URL或本地文件路径> [选项]")
        print()
        print("选项:")
        print("  --browser <类型>  从浏览器读取 SESSDATA (auto, chrome, edge, firefox, brave)")
        print("  --model <大小>     Whisper 模型大小 (base, small, medium, large, large-v3)")
        print()
        print("支持的格式:")
        print("  - B站视频URL (如: https://www.bilibili.com/video/BV1xx...)")
        print("  - 本地音频文件 (mp3, wav, m4a, aac, flac, ogg, wma, opus)")
        print("  - 本地视频文件 (mp4, avi, mkv, mov, flv, wmv, webm, m4v)")
        sys.exit(1)

    # 解析参数
    input_arg = None
    browser = "auto"  # 默认自动从浏览器读取
    model_size = "large-v3"

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--browser":
            if i + 1 < len(sys.argv):
                browser = sys.argv[i + 1]
                i += 2
            else:
                print("错误: --browser 参数需要指定浏览器类型")
                sys.exit(1)
        elif arg == "--model":
            if i + 1 < len(sys.argv):
                model_size = sys.argv[i + 1]
                i += 2
            else:
                print("错误: --model 参数需要指定模型大小")
                sys.exit(1)
        else:
            input_arg = arg
            i += 1

    if not input_arg:
        print("错误: 请提供 B站视频URL或本地文件路径")
        sys.exit(1)

    # 验证模型大小
    valid_models = ["base", "small", "medium", "large", "large-v3"]
    if model_size not in valid_models:
        print(f"警告: 无效的模型大小 '{model_size}'，使用默认 'large-v3' 模型")
        model_size = "large-v3"

    # 判断是本地文件还是 B站 URL
    is_local_file = os.path.exists(input_arg)

    if is_local_file:
        # 本地文件 ASR 模式
        file_title = os.path.splitext(os.path.basename(input_arg))[0]
        print(f"{'='*60}")
        print(f"文件名称: {file_title}")
        print(f"字幕来源: Whisper ASR语音识别 (AI生成)")
        print(f"{'='*60}\n")

        result = asyncio.run(transcribe_file_with_asr(
            input_arg,
            ResponseFormat.TEXT,
            model_size
        ))

        print_result(result)
        return

    # B站 URL 模式
    video_url = input_arg

    # 检查并获取 SESSDATA
    sessdata, source = get_sessdata_with_source(browser=browser)

    if not sessdata:
        print("[bilibili-captions] ✗ 错误: 未找到 SESSDATA", file=sys.stderr)
        print("[bilibili-captions] 提示: 请设置环境变量 BILIBILI_SESSDATA 或确保浏览器已登录 B站", file=sys.stderr)
        sys.exit(1)

    # 下载字幕（API优先，ASR兜底）
    result = asyncio.run(download_subtitles_with_asr(
        video_url,
        ResponseFormat.TEXT,
        model_size,
        sessdata
    ))

    # 打印结果（包含视频标题框）
    print_result(result)


if __name__ == "__main__":
    main()
