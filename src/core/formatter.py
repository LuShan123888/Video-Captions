"""
字幕格式化 - 将字幕数据格式化为 text/srt/json 格式
"""

from typing import Dict, Any, List
from enum import Enum

from .text import convert_to_simplified


class ResponseFormat(str, Enum):
    """响应格式枚举"""
    TEXT = "text"
    SRT = "srt"
    JSON = "json"


CHARACTER_LIMIT = 50000


def format_subtitle(
    segments: List[Dict[str, Any]],
    video_title: str,
    format: ResponseFormat,
    source: str = "api",
    language: str = None
) -> Dict[str, Any]:
    """将字幕数据格式化为指定格式

    Args:
        segments: 字幕片段列表 [{"start": 0.0, "end": 1.0, "content/text": "..."}]
        video_title: 视频标题
        format: 输出格式 (text/srt/json)
        source: 来源标识 (api/whisper_asr)
        language: 语言代码（可选）

    Returns:
        格式化后的字幕数据
    """
    if format == ResponseFormat.JSON:
        converted_data = [
            {
                "from": seg['start'],
                "to": seg['end'],
                "content": convert_to_simplified(seg.get('content', seg.get('text', '')))
            }
            for seg in segments
        ]
        result = {
            "source": source,
            "format": "json",
            "subtitle_count": len(segments),
            "subtitles": converted_data,
            "video_title": video_title
        }
        if language:
            result["language"] = language
        return result

    elif format == ResponseFormat.SRT:
        srt_content = ""
        for i, seg in enumerate(segments):
            start = seg['start']
            end = seg['end']
            text = seg.get('content', seg.get('text', ''))

            start_h = int(start // 3600)
            start_m = int((start % 3600) // 60)
            start_s = start % 60
            end_h = int(end // 3600)
            end_m = int((end % 3600) // 60)
            end_s = end % 60

            srt_content += f"{i + 1}\n"
            srt_content += f"{start_h:02}:{start_m:02}:{start_s:06.3f}".replace('.', ',')
            srt_content += f" --> {end_h:02}:{end_m:02}:{end_s:06.3f}".replace('.', ',')
            srt_content += f"\n{text}\n\n"

        srt_content = convert_to_simplified(srt_content)
        result = {
            "source": source,
            "format": "srt",
            "subtitle_count": len(segments),
            "content": srt_content,
            "video_title": video_title
        }
        if language:
            result["language"] = language
        return result

    else:  # TEXT format
        text_lines = [seg.get('content', seg.get('text', '')) for seg in segments]
        text_content = '\n'.join(text_lines)

        if len(text_content) > CHARACTER_LIMIT:
            text_content = text_content[:CHARACTER_LIMIT] + "\n\n... (内容已截断)"

        text_content = convert_to_simplified(text_content)

        result = {
            "source": source,
            "format": "text",
            "subtitle_count": len(segments),
            "content": text_content,
            "video_title": video_title
        }
        if language:
            result["language"] = language
        return result
