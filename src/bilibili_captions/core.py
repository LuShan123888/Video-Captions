# /// script
# dependencies = ["httpx", "mlx-whisper", "opencc-python-reimplemented"]
# -*-

"""
B站API封装模块 - 为MCP服务器和CLI提供共享功能
"""

import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
from typing import Optional, Dict, Any
from enum import Enum

# 设置环境变量确保UTF-8编码（必须在其他导入之前）
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 确保stdout/stderr使用UTF-8编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# ============================================================================
# 日志系统
# ============================================================================

_verbose_log = False


def set_verbose_log(enabled: bool = True) -> None:
    """启用/禁用详细日志"""
    global _verbose_log
    _verbose_log = enabled


def log_info(message: str) -> None:
    """打印信息日志"""
    print(f"[bilibili-captions] {message}", file=sys.stderr)


def log_step(step: str, message: str = "") -> None:
    """打印步骤日志"""
    if message:
        print(f"[bilibili-captions] ▶ {step}: {message}", file=sys.stderr)
    else:
        print(f"[bilibili-captions] ▶ {step}", file=sys.stderr)


def log_success(message: str) -> None:
    """打印成功日志"""
    print(f"[bilibili-captions] ✓ {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    """打印警告日志"""
    print(f"[bilibili-captions] ⚠ {message}", file=sys.stderr)


def log_error(message: str) -> None:
    """打印错误日志"""
    print(f"[bilibili-captions] ✗ {message}", file=sys.stderr)


def log_debug(message: str) -> None:
    """打印调试日志（仅在详细模式下）"""
    if _verbose_log:
        print(f"[bilibili-captions]   └─ {message}", file=sys.stderr)

import httpx
from tqdm import tqdm
from opencc import OpenCC

# 常量
API_BASE_URL = "https://api.bilibili.com"
CHARACTER_LIMIT = 50000


class ResponseFormat(str, Enum):
    """响应格式枚举"""
    TEXT = "text"
    SRT = "srt"
    JSON = "json"


def make_safe_filename(filename: str) -> str:
    """移除或替换文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def get_sessdata(
        sessdata: Optional[str] = None,
        browser: Optional[str] = "auto"
) -> Optional[str]:
    """获取SESSDATA，按优先级从参数、环境变量、浏览器读取

    Args:
        sessdata: 直接传入的SESSDATA
        browser: 指定从哪个浏览器读取 ("auto", "chrome", "edge", "firefox", "brave", None)
                  默认为 "auto"，设为 None 可禁用浏览器读取

    Returns:
        SESSDATA字符串，如果都未找到则返回None
    """
    result, _ = get_sessdata_with_source(sessdata, browser, log=False)
    return result


def get_sessdata_with_source(
        sessdata: Optional[str] = None,
        browser: Optional[str] = "auto",
        log: bool = True
) -> tuple[Optional[str], Optional[str]]:
    """获取SESSDATA及其来源，按优先级从参数、环境变量、浏览器读取

    Args:
        sessdata: 直接传入的SESSDATA
        browser: 指定从哪个浏览器读取 ("auto", "chrome", "edge", "firefox", "brave", None)
                  默认为 "auto"，设为 None 可禁用浏览器读取
        log: 是否打印日志（默认 True）

    Returns:
        (SESSDATA字符串, 来源描述)，如果都未找到则返回(None, None)
        来源描述: "parameter" | "env" | "browser:{name}" | None
    """
    if log:
        log_step("获取 SESSDATA")

    # 1. 使用传入的参数
    if log:
        log_debug("检查参数传入...")
    if sessdata:
        if log:
            log_success("从参数获取 SESSDATA")
        return sessdata, "parameter"
    if log:
        log_debug("参数未传入")

    # 2. 从环境变量读取
    if log:
        log_debug("检查环境变量 BILIBILI_SESSDATA...")
    env_sessdata = os.environ.get('BILIBILI_SESSDATA')
    if env_sessdata:
        if log:
            log_success("从环境变量获取 SESSDATA")
        return env_sessdata, "env"
    if log:
        log_debug("环境变量未设置")

    # 3. 从浏览器读取（如果启用）
    if browser is not False:  # 允许显式禁用浏览器读取
        if log:
            log_debug(f"尝试从浏览器读取 (模式: {browser or 'auto'})...")
        from .browser import get_sessdata_from_browser, get_browser_name
        browser_sessdata = get_sessdata_from_browser(browser or "auto", log=log)
        if browser_sessdata:
            detected_browser = get_browser_name(browser or "auto")
            if log:
                log_success(f"从浏览器获取 SESSDATA ({detected_browser})")
            return browser_sessdata, f"browser:{detected_browser}"
        if log:
            log_debug("浏览器未找到 SESSDATA")
    else:
        if log:
            log_debug("浏览器读取已禁用")

    # 没有找到SESSDATA，返回None
    if log:
        log_warning("未获取到 SESSDATA")
    return None, None


def require_sessdata(
        sessdata: Optional[str] = None,
        browser: Optional[str] = "auto"
) -> str:
    """获取SESSDATA，如果没有找到则抛出异常

    Args:
        sessdata: 直接传入的SESSDATA
        browser: 指定从哪个浏览器读取 ("auto", "chrome", "edge", "firefox", "brave", None)
                  默认为 "auto"，设为 None 可禁用浏览器读取

    Returns:
        SESSDATA字符串

    Raises:
        ValueError: 如果没有找到SESSDATA
    """
    result = get_sessdata(sessdata, browser)
    if not result:
        raise ValueError(
            "未找到B站SESSDATA认证信息。请通过以下方式之一提供：\n"
            "1. 在浏览器中登录 B站（推荐，默认会自动读取）\n"
            "2. 设置环境变量 BILIBILI_SESSDATA\n"
            "3. 调用时传入 sessdata 参数"
        )
    return result


def extract_bvid(url: str) -> str:
    """从URL中提取BV号

    支持多种URL格式:
    - https://www.bilibili.com/video/BV1xx411c7mD/
    - https://www.bilibili.com/list/watchlater/?bvid=BV16HqFBZE6N
    - BV1xx411c7mD
    """
    # 直接BV号
    if url.startswith('BV'):
        return url

    # 从URL路径提取
    if '/video/' in url:
        path = url.split('/video/')[1].split('/')[0]
        return path.rstrip('/')

    # 从查询参数提取 (稍后观看列表等)
    if 'bvid=' in url or 'BVID=' in url:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        bvid = params.get('bvid') or params.get('BVID')
        if bvid:
            return bvid[0]

    # 从URL最后一段提取（可能是短链接或直接BV号）
    last_part = url.rstrip('/').split('/')[-1]
    # 移除查询参数
    if '?' in last_part:
        last_part = last_part.split('?')[0]

    if last_part.startswith('BV'):
        return last_part

    raise ValueError(f"无法从URL中提取BV号: {url}")


async def get_video_info(url: str, sessdata: Optional[str] = None) -> Dict[str, Any]:
    """获取B站视频的基本信息

    Args:
        url: B站视频URL
        sessdata: 可选的SESSDATA认证

    Returns:
        包含视频信息的字典:
        {
            "title": "视频标题",
            "bvid": "BV号",
            "cid": "分P ID",
            "duration": 180,  # 秒
            "description": "视频简介",
            "owner": {"name": "UP主", "mid": "用户ID"},
            "has_subtitle": true
        }

    Raises:
        ValueError: 无法获取视频信息
    """
    bvid = extract_bvid(url)
    info_api_url = f"{API_BASE_URL}/x/web-interface/view?bvid={bvid}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com/'
    }

    cookies = {}
    sess = get_sessdata(sessdata)
    if sess:
        cookies['SESSDATA'] = sess

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(info_api_url, headers=headers, cookies=cookies)
        response.raise_for_status()
        data = response.json()

    if data['code'] != 0:
        raise ValueError(f"B站API返回错误: {data.get('message', '未知错误')}")

    video_data = data['data']
    return {
        "title": video_data.get('title'),
        "bvid": video_data.get('bvid'),
        "cid": video_data.get('cid'),
        "duration": video_data.get('duration', 0),
        "description": video_data.get('desc', ''),
        "owner": {
            "name": video_data.get('owner', {}).get('name'),
            "mid": video_data.get('owner', {}).get('mid')
        },
        "has_subtitle": bool(video_data.get('subtitle', {}).get('list'))
    }


async def list_subtitles(url: str, sessdata: Optional[str] = None) -> Dict[str, Any]:
    """列出视频可用的字幕

    Args:
        url: B站视频URL
        sessdata: 可选的SESSDATA认证

    Returns:
        {
            "available": true,
            "subtitles": [{"lan": "ai-zh", "lan_doc": "中文（AI生成）", "subtitle_url": "..."}],
            "subtitle_count": 1
        }
    """
    video_info = await get_video_info(url, sessdata)
    bvid = video_info['bvid']
    cid = video_info['cid']

    subtitle_api_url = f"{API_BASE_URL}/x/player/wbi/v2?bvid={bvid}&cid={cid}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': f'https://www.bilibili.com/video/{bvid}',
    }

    cookies = {}
    sess = get_sessdata(sessdata)
    if sess:
        cookies['SESSDATA'] = sess

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(subtitle_api_url, headers=headers, cookies=cookies)
        response.raise_for_status()
        data = response.json()

    if data['code'] != 0:
        return {
            "available": False,
            "subtitles": [],
            "subtitle_count": 0,
            "error": data.get('message', '未知错误')
        }

    subtitle_data = data['data'].get('subtitle', {})
    subtitle_list = subtitle_data.get('subtitles', [])

    subtitles = []
    for sub in subtitle_list:
        subtitles.append({
            "lan": sub.get('lan'),
            "lan_doc": sub.get('lan_doc'),
            "subtitle_url": sub.get('subtitle_url')
        })

    return {
        "available": len(subtitles) > 0,
        "subtitles": subtitles,
        "subtitle_count": len(subtitles)
    }


async def download_subtitle_content(
        url: str,
        format: ResponseFormat = ResponseFormat.TEXT,
        sessdata: Optional[str] = None
) -> Dict[str, Any]:
    """下载视频字幕内容

    Args:
        url: B站视频URL
        format: 输出格式 (text/srt/json)
        sessdata: 可选的SESSDATA认证

    Returns:
        {
            "source": "bilibili_api",
            "format": "text",
            "subtitle_count": 173,
            "content": "字幕内容...",
            "video_title": "视频标题"
        }
    """
    try:
        # 先获取字幕列表
        log_debug("获取字幕列表...")
        subtitle_info = await list_subtitles(url, sessdata)

        if not subtitle_info['available']:
            log_debug("该视频没有可用字幕")
            return {
                "error": "该视频没有可用字幕",
                "suggestion": "对于无字幕视频，可以使用 ASR 功能生成字幕"
            }

        log_debug(f"找到 {len(subtitle_info['subtitles'])} 个字幕")

        # 选择中文AI字幕
        zh_subtitle = None
        for sub in subtitle_info['subtitles']:
            if sub['lan'] in ['ai-zh', 'zh-Hans', 'zh-CN', 'zh']:
                zh_subtitle = sub
                break

        if not zh_subtitle:
            zh_subtitle = subtitle_info['subtitles'][0]

        log_debug(f"选择字幕: {zh_subtitle.get('lan', 'unknown')} - {zh_subtitle.get('lan_doc', '')}")

        # 获取视频信息
        log_debug("获取视频信息...")
        video_info = await get_video_info(url, sessdata)

        # 下载字幕内容
        log_debug("下载字幕文件...")
        subtitle_url = zh_subtitle['subtitle_url']
        if not subtitle_url.startswith('http'):
            subtitle_url = 'https:' + subtitle_url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(subtitle_url, headers=headers)
            response.raise_for_status()
            subtitle_json = response.json()

        body = subtitle_json.get('body', [])
        log_success(f"API 获取成功，共 {len(body)} 条字幕")

        # 根据格式返回内容
        if format == ResponseFormat.JSON:
            # 繁简转换 JSON 内容
            converted_body = [
                {**item, "content": convert_to_simplified(item.get("content", ""))}
                for item in body
            ]
            return {
                "source": "bilibili_api",
                "format": "json",
                "subtitle_count": len(body),
                "subtitles": converted_body,
                "video_title": video_info['title']
            }

        elif format == ResponseFormat.SRT:
            srt_content = ""
            for i, item in enumerate(body):
                start_time = item['from']
                end_time = item['to']
                content = item['content']

                start_h, start_m, start_s = int(start_time // 3600), int((start_time % 3600) // 60), start_time % 60
                end_h, end_m, end_s = int(end_time // 3600), int((end_time % 3600) // 60), end_time % 60

                srt_content += f"{i + 1}\n"
                srt_content += f"{start_h:02}:{start_m:02}:{start_s:06.3f}".replace('.', ',')
                srt_content += f" --> {end_h:02}:{end_m:02}:{end_s:06.3f}".replace('.', ',')
                srt_content += f"\n{content}\n\n"

            # 繁简转换
            srt_content = convert_to_simplified(srt_content)
            return {
                "source": "bilibili_api",
                "format": "srt",
                "subtitle_count": len(body),
                "content": srt_content,
                "video_title": video_info['title']
            }

        else:  # TEXT format
            text_lines = [item['content'] for item in body]
            text_content = '\n'.join(text_lines)

            # 检查字符限制
            if len(text_content) > CHARACTER_LIMIT:
                text_content = text_content[:CHARACTER_LIMIT] + "\n\n... (内容已截断)"

            # 繁简转换
            text_content = convert_to_simplified(text_content)

            return {
                "source": "bilibili_api",
                "format": "text",
                "subtitle_count": len(body),
                "content": text_content,
                "video_title": video_info['title']
            }

    except UnicodeEncodeError as e:
        # 捕获编码错误并返回更友好的错误信息
        return {
            "error": "encoding_error",
            "message": f"字符编码错误: {str(e)}",
            "suggestion": "请确保系统使用UTF-8编码"
        }
    except Exception as e:
        return {
            "error": f"下载字幕时发生错误: {type(e).__name__}",
            "message": str(e)
        }


def convert_to_simplified(text: str) -> str:
    """将繁体中文转换为简体中文"""
    try:
        cc = OpenCC('t2s')
        return cc.convert(text)
    except (TypeError, ValueError, RuntimeError):
        return text


async def transcribe_with_asr(
        audio_file: str,
        model_size: str = "large-v3",
        show_progress: bool = True
) -> Dict[str, Any]:
    """使用Whisper ASR生成字幕

    使用 mlx-whisper 进行语音识别（针对 Apple Silicon 优化）。

    Args:
        audio_file: 音频文件路径
        model_size: 模型大小 (base/small/medium/large/large-v3)
        show_progress: 是否显示进度条

    Returns:
        {
            "source": "whisper_asr",
            "segments": [...],
            "language": "zh",
            "duration": 180.5
        }
    """
    # 延迟导入 mlx_whisper（加载较慢）
    import mlx_whisper

    # 模型映射：model_size -> mlx-community 模型名
    model_map = {
        "base": "mlx-community/whisper-base-mlx",
        "small": "mlx-community/whisper-small-mlx",
        "medium": "mlx-community/whisper-medium-mlx",
        "large": "mlx-community/whisper-large-v3-mlx",
        "large-v3": "mlx-community/whisper-large-v3-mlx",
    }

    model_path = model_map.get(model_size, "mlx-community/whisper-large-v3-mlx")

    if show_progress:
        log_step(f"加载 Whisper {model_size} 模型", "(mlx-whisper)")

    start_time = time.time()

    # 使用 mlx_whisper 进行转录
    result = mlx_whisper.transcribe(
        audio_file,
        path_or_hf_repo=model_path,
        language="zh",
        hallucination_silence_threshold=0.5,
        condition_on_previous_text=False,
        verbose=show_progress,
    )

    elapsed = time.time() - start_time

    # 解析结果
    segments = result.get("segments", [])
    segment_list = []
    text_lines = []

    for seg in segments:
        segment_list.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        })
        text_lines.append(seg["text"].strip())

    return {
        "source": "whisper_asr",
        "segments": segment_list,
        "text": '\n'.join(text_lines),
        "language": result.get("language", "zh"),
        "duration": elapsed
    }


async def download_and_extract_audio(
        url: str,
        output_dir: str,
        show_progress: bool = True
) -> tuple[str, str, str]:
    """下载B站视频并提取音频

    Args:
        url: B站视频URL
        output_dir: 输出目录
        show_progress: 是否显示进度提示

    Returns:
        (audio_file, video_title, bvid) - 音频文件路径、视频标题、BV号

    Raises:
        subprocess.CalledProcessError: 下载或提取失败
    """
    # 获取视频信息
    info = await get_video_info(url)
    video_title = info.get("title", "video")
    bvid = info.get("bvid", extract_bvid(url))

    safe_title = make_safe_filename(video_title)
    video_filename = os.path.join(output_dir, f"{safe_title}.mp4")
    audio_filename = os.path.join(output_dir, f"{safe_title}.wav")

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 如果音频已存在，直接返回
    if os.path.exists(audio_filename):
        return audio_filename, video_title, bvid

    # 始终构建标准视频URL（yt-dlp 不支持稍后观看等特殊URL）
    url = f"https://www.bilibili.com/video/{bvid}"

    # 使用 yt-dlp 下载视频
    if not os.path.exists(video_filename):
        if show_progress:
            log_step("正在下载视频")
        subprocess.run(
            ['yt-dlp', '-o', video_filename, url],
            check=True,
            capture_output=True
        )

    # 使用 ffmpeg 提取音频
    if show_progress:
        log_step("正在提取音频")
    subprocess.run(
        ['ffmpeg', '-y', '-i', video_filename, '-vn',
         '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_filename],
        check=True,
        capture_output=True
    )

    return audio_filename, video_title, bvid


def is_video_file(file_path: str) -> bool:
    """判断文件是否为视频格式"""
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg'}
    return os.path.splitext(file_path)[1].lower() in video_extensions


def is_audio_file(file_path: str) -> bool:
    """判断文件是否为音频格式"""
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma', '.opus'}
    return os.path.splitext(file_path)[1].lower() in audio_extensions


async def extract_audio_from_video(
        video_file: str,
        output_dir: str,
        show_progress: bool = True
) -> str:
    """从视频文件中提取音频

    Args:
        video_file: 视频文件路径
        output_dir: 输出目录
        show_progress: 是否显示进度提示

    Returns:
        音频文件路径
    """
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    audio_filename = os.path.join(output_dir, f"{base_name}.wav")

    # 如果音频已存在，直接返回
    if os.path.exists(audio_filename):
        return audio_filename

    os.makedirs(output_dir, exist_ok=True)

    if show_progress:
        print("正在从视频提取音频...")

    subprocess.run(
        ['ffmpeg', '-y', '-i', video_file, '-vn',
         '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_filename],
        check=True,
        capture_output=True
    )

    return audio_filename


async def transcribe_file_with_asr(
        file_path: str,
        format: ResponseFormat = ResponseFormat.TEXT,
        model_size: str = "medium",
        show_progress: bool = True
) -> Dict[str, Any]:
    """对本地音频/视频文件进行 ASR 转录

    Args:
        file_path: 本地文件路径（支持音频和视频格式）
        format: 输出格式 (text/srt/json)
        model_size: Whisper模型大小 (base/small/medium/large/large-v3)
        show_progress: 是否显示进度条

    Returns:
        {
            "source": "whisper_asr",
            "format": str,
            "subtitle_count": int,
            "content": str,  # text/srt格式
            "video_title": str  # 文件名
        }
    """
    if not os.path.exists(file_path):
        return {
            "error": "文件不存在",
            "message": f"文件不存在: {file_path}"
        }

    file_title = os.path.splitext(os.path.basename(file_path))[0]

    try:
        # 如果是视频文件，先提取音频
        if is_video_file(file_path):
            with tempfile.TemporaryDirectory() as temp_dir:
                audio_file = await extract_audio_from_video(file_path, temp_dir, show_progress)
                asr_result = await transcribe_with_asr(audio_file, model_size, show_progress)
        # 如果是音频文件，直接使用
        elif is_audio_file(file_path):
            audio_file = file_path
            asr_result = await transcribe_with_asr(audio_file, model_size, show_progress)
        else:
            return {
                "error": "不支持的文件格式",
                "message": f"不支持的文件格式: {os.path.splitext(file_path)[1]}",
                "suggestion": "支持的音频格式: mp3, wav, m4a, aac, flac, ogg, wma, opus"
                            "支持的视频格式: mp4, avi, mkv, mov, flv, wmv, webm, m4v, mpg, mpeg"
            }

        # 转换为请求的格式
        segments = asr_result.get("segments", [])

        if format == ResponseFormat.JSON:
            return {
                "source": "whisper_asr",
                "format": "json",
                "subtitle_count": len(segments),
                "subtitles": [
                    {
                        "from": seg["start"],
                        "to": seg["end"],
                        "content": convert_to_simplified(seg["text"])
                    }
                    for seg in segments
                ],
                "video_title": file_title
            }

        elif format == ResponseFormat.SRT:
            srt_content = ""
            for i, seg in enumerate(segments):
                start = seg["start"]
                end = seg["end"]
                text = seg["text"]

                start_h, start_m, start_s = int(start // 3600), int((start % 3600) // 60), start % 60
                end_h, end_m, end_s = int(end // 3600), int((end % 3600) // 60), end % 60

                srt_content += f"{i + 1}\n"
                srt_content += f"{start_h:02}:{start_m:02}:{start_s:06.3f}".replace('.', ',')
                srt_content += f" --> {end_h:02}:{end_m:02}:{end_s:06.3f}".replace('.', ',')
                srt_content += f"\n{text}\n\n"

            # 繁简转换
            srt_content = convert_to_simplified(srt_content)
            return {
                "source": "whisper_asr",
                "format": "srt",
                "subtitle_count": len(segments),
                "content": srt_content,
                "video_title": file_title
            }

        else:  # TEXT
            text_content = '\n'.join(seg["text"] for seg in segments)
            # 繁简转换
            text_content = convert_to_simplified(text_content)
            return {
                "source": "whisper_asr",
                "format": "text",
                "subtitle_count": len(segments),
                "content": text_content,
                "video_title": file_title
            }

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else ''
        return {
            "error": f"ASR转录失败: {type(e).__name__}",
            "message": str(e),
            "stderr": stderr[:200] if stderr else None,
            "suggestion": "请确保已安装 ffmpeg: brew install ffmpeg"
        }
    except FileNotFoundError:
        return {
            "error": "ASR转录失败: FileNotFoundError",
            "message": "未找到必要的命令行工具",
            "suggestion": "请安装 ffmpeg: brew install ffmpeg"
        }
    except Exception as e:
        return {
            "error": f"ASR转录失败: {type(e).__name__}",
            "message": str(e)
        }


async def download_subtitles_with_asr(
        url: str,
        format: ResponseFormat = ResponseFormat.TEXT,
        model_size: str = "medium",
        sessdata: Optional[str] = None,
        show_progress: bool = True
) -> Dict[str, Any]:
    """下载字幕，优先使用API，无字幕时使用ASR生成

    Args:
        url: B站视频URL
        format: 输出格式 (text/srt/json)
        model_size: Whisper模型大小 (base/small/medium/large)
        sessdata: SESSDATA认证
        show_progress: 是否显示进度条（CLI 使用，MCP 服务器可禁用）

    Returns:
        与 download_subtitle_content 相同格式，但 source 可能是 "whisper_asr"
    """
    log_step("下载字幕", f"URL: {url[:50]}...")

    # 先尝试从API获取
    result = await download_subtitle_content(url, format, sessdata)

    # 如果有错误（无字幕），使用ASR兜底
    if "error" in result:
        log_warning(f"API 无字幕: {result.get('error', '未知错误')}")
        log_step("切换到 ASR 模式", f"模型: {model_size}")

        # 使用临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # 下载视频并提取音频
                log_step("下载视频并提取音频")
                audio_file, video_title, bvid = await download_and_extract_audio(
                    url, temp_dir, show_progress
                )
                log_success(f"音频提取完成: {os.path.basename(audio_file)}")

                # 打印视频标题框（ASR 输出前）
                print(f"{'='*60}")
                print(f"视频标题: {video_title}")
                print(f"{'='*60}\n")

                # 使用ASR生成字幕
                log_step("ASR 语音识别", "这可能需要几分钟...")
                asr_result = await transcribe_with_asr(audio_file, model_size, show_progress)

                # 转换为请求的格式
                segments = asr_result.get("segments", [])
                log_success(f"ASR 完成，共 {len(segments)} 个片段")

                if format == ResponseFormat.JSON:
                    return {
                        "source": "whisper_asr",
                        "format": "json",
                        "subtitle_count": len(segments),
                        "subtitles": [
                            {
                                "from": seg["start"],
                                "to": seg["end"],
                                "content": convert_to_simplified(seg["text"])
                            }
                            for seg in segments
                        ],
                        "video_title": video_title
                    }

                elif format == ResponseFormat.SRT:
                    srt_content = ""
                    for i, seg in enumerate(segments):
                        start = seg["start"]
                        end = seg["end"]
                        text = seg["text"]

                        start_h, start_m, start_s = int(start // 3600), int((start % 3600) // 60), start % 60
                        end_h, end_m, end_s = int(end // 3600), int((end % 3600) // 60), end % 60

                        srt_content += f"{i + 1}\n"
                        srt_content += f"{start_h:02}:{start_m:02}:{start_s:06.3f}".replace('.', ',')
                        srt_content += f" --> {end_h:02}:{end_m:02}:{end_s:06.3f}".replace('.', ',')
                        srt_content += f"\n{text}\n\n"

                    # 繁简转换
                    srt_content = convert_to_simplified(srt_content)
                    return {
                        "source": "whisper_asr",
                        "format": "srt",
                        "subtitle_count": len(segments),
                        "content": srt_content,
                        "video_title": video_title
                    }

                else:  # TEXT
                    text_content = '\n'.join(seg["text"] for seg in segments)
                    # 繁简转换
                    text_content = convert_to_simplified(text_content)
                    return {
                        "source": "whisper_asr",
                        "format": "text",
                        "subtitle_count": len(segments),
                        "content": text_content,
                        "video_title": video_title
                    }

            except subprocess.CalledProcessError as e:
                # 解析错误输出以获取更具体的信息
                stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else ''
                suggestion = "请检查网络连接和视频可访问性"

                if 'command not found' in stderr.lower() or 'not found' in stderr.lower():
                    suggestion = "请确保已安装 yt-dlp: brew install yt-dlp"
                elif 'ffmpeg' in stderr.lower():
                    suggestion = "请确保已安装 ffmpeg: brew install ffmpeg"
                elif 'sign' in stderr.lower() or 'login' in stderr.lower() or 'access' in stderr.lower():
                    suggestion = "该视频可能需要登录或为会员专享，请设置 SESSDATA"
                elif 'unsupported' in stderr.lower() or 'no video' in stderr.lower():
                    suggestion = "该视频格式不支持或无法访问"
                elif 'http' in stderr.lower():
                    suggestion = "网络请求失败，请检查网络连接或稍后重试"

                return {
                    "error": f"ASR生成字幕失败: {type(e).__name__}",
                    "message": str(e),
                    "stderr": stderr[:200] if stderr else None,
                    "suggestion": suggestion
                }
            except FileNotFoundError:
                return {
                    "error": "ASR生成字幕失败: FileNotFoundError",
                    "message": "未找到必要的命令行工具",
                    "suggestion": "请安装 yt-dlp 和 ffmpeg: brew install yt-dlp ffmpeg"
                }
            except Exception as e:
                return {
                    "error": f"ASR生成字幕失败: {type(e).__name__}",
                    "message": str(e),
                    "suggestion": f"请确保已安装 yt-dlp 和 ffmpeg，且视频可正常访问"
                }

    return result
