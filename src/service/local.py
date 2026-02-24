"""
本地文件服务 - 处理本地音频/视频文件的 ASR 转录
"""

import os
import subprocess
import tempfile
from typing import Dict, Any, Optional

from .base import SubtitleService
from core.formatter import ResponseFormat, format_subtitle
from core.audio import extract_audio, is_video_file, is_audio_file
from core.asr import transcribe_with_asr
from core.logging import log_step, log_success


class LocalService(SubtitleService):
    """本地文件字幕服务"""

    @property
    def name(self) -> str:
        return "local"

    def is_supported(self, source: str) -> bool:
        """判断是否为本地文件"""
        if os.path.isabs(source) or source.startswith('./') or source.startswith('../'):
            return os.path.exists(source) and (is_video_file(source) or is_audio_file(source))
        return os.path.exists(source) and (is_video_file(source) or is_audio_file(source))

    async def get_info(self, source: str) -> Dict[str, Any]:
        """获取文件信息"""
        if not os.path.exists(source):
            return {"error": "文件不存在", "message": f"文件不存在: {source}"}

        file_title = os.path.splitext(os.path.basename(source))[0]
        return {
            "title": file_title,
            "id": file_title,
            "file_path": source,
            "file_size": os.path.getsize(source),
            "file_type": "video" if is_video_file(source) else "audio",
            "has_subtitle": False
        }

    async def list_subtitles(self, source: str) -> Dict[str, Any]:
        """本地文件没有预置字幕"""
        return {"available": False, "subtitles": [], "subtitle_count": 0}

    async def download_subtitle(
        self,
        source: str,
        format: ResponseFormat = ResponseFormat.TEXT,
        model_size: str = "large",
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """对本地音频/视频文件进行 ASR 转录"""
        if not os.path.exists(source):
            return {"error": "文件不存在", "message": f"文件不存在: {source}"}

        file_title = os.path.splitext(os.path.basename(source))[0]

        # 打印文件信息
        print(f"{'='*60}")
        print(f"文件名称: {file_title}")
        print(f"字幕来源: Whisper ASR语音识别 (AI生成)")
        print(f"{'='*60}\n")

        try:
            if is_video_file(source):
                with tempfile.TemporaryDirectory() as temp_dir:
                    log_step("提取音频")
                    audio_file = extract_audio(source, temp_dir, show_progress)
                    log_step("ASR 语音识别", "这可能需要几分钟...")
                    asr_result = await transcribe_with_asr(audio_file, model_size, show_progress)
            elif is_audio_file(source):
                log_step("ASR 语音识别", "这可能需要几分钟...")
                asr_result = await transcribe_with_asr(source, model_size, show_progress)
            else:
                return {
                    "error": "不支持的文件格式",
                    "message": f"不支持的文件格式: {os.path.splitext(source)[1]}",
                    "suggestion": "支持的音频格式: mp3, wav, m4a, aac, flac, ogg, wma, opus; "
                                  "支持的视频格式: mp4, avi, mkv, mov, flv, wmv, webm, m4v"
                }

            segments = asr_result.get("segments", [])
            log_success(f"ASR 完成，共 {len(segments)} 个片段")

            formatted = [
                {"start": seg["start"], "end": seg["end"], "content": seg["text"]}
                for seg in segments
            ]

            return format_subtitle(formatted, file_title, format, source="whisper_asr")

        except subprocess.CalledProcessError as e:
            stderr = e.stderr if isinstance(e.stderr, str) else e.stderr.decode('utf-8', errors='ignore') if e.stderr else ''
            return {
                "error": "ASR转录失败",
                "message": str(e),
                "stderr": stderr[:200] if stderr else None,
                "suggestion": "请确保已安装 ffmpeg: brew install ffmpeg"
            }
        except Exception as e:
            return {"error": f"ASR转录失败: {type(e).__name__}", "message": str(e)}

    async def download_video(
        self,
        source: str,
        output_dir: str,
        show_progress: bool = True
    ) -> tuple[str, str, str]:
        """本地文件不需要下载，直接返回文件路径"""
        if not os.path.exists(source):
            raise FileNotFoundError(f"文件不存在: {source}")

        file_title = os.path.splitext(os.path.basename(source))[0]
        return source, file_title, file_title

    def extract_audio(
        self,
        video_file: str,
        output_dir: Optional[str] = None,
        show_progress: bool = True
    ) -> str:
        """从视频文件中提取音频"""
        return extract_audio(video_file, output_dir, show_progress)
