"""
Service 层基类 - 定义所有字幕服务必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from core.formatter import ResponseFormat


class SubtitleService(ABC):
    """字幕服务抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """服务名称"""
        pass

    @abstractmethod
    def is_supported(self, source: str) -> bool:
        """判断是否支持该来源（URL 或文件路径）

        Args:
            source: 视频来源（URL 或本地文件路径）

        Returns:
            是否支持该来源
        """
        pass

    @abstractmethod
    async def get_info(self, source: str) -> Dict[str, Any]:
        """获取视频/文件信息

        Args:
            source: 视频来源

        Returns:
            {
                "title": "标题",
                "id": "ID",
                "duration": 180,  # 秒
                "description": "简介",
                "author": "作者",
                "has_subtitle": true
            }
        """
        pass

    @abstractmethod
    async def list_subtitles(self, source: str) -> Dict[str, Any]:
        """列出可用的字幕

        Args:
            source: 视频来源

        Returns:
            {
                "available": true,
                "subtitles": [{"lan": "zh-Hans", "lan_doc": "中文（简体）"}],
                "subtitle_count": 1
            }
        """
        pass

    @abstractmethod
    async def download_subtitle(
        self,
        source: str,
        format: ResponseFormat = ResponseFormat.TEXT
    ) -> Dict[str, Any]:
        """下载字幕（API 优先，ASR 兜底）

        Args:
            source: 视频来源
            format: 输出格式 (text/srt/json)

        Returns:
            {
                "source": "api" | "whisper_asr",
                "format": "text",
                "subtitle_count": 173,
                "content": "字幕内容...",
                "video_title": "视频标题"
            }
        """
        pass

    @abstractmethod
    async def download_video(
        self,
        source: str,
        output_dir: str,
        show_progress: bool = True
    ) -> tuple[str, str, str]:
        """下载视频

        Args:
            source: 视频来源
            output_dir: 输出目录
            show_progress: 是否显示进度提示

        Returns:
            (video_file, video_title, video_id) - 视频文件路径、视频标题、视频ID
        """
        pass

    @abstractmethod
    def extract_audio(
        self,
        video_file: str,
        output_dir: Optional[str] = None,
        show_progress: bool = True
    ) -> str:
        """从视频文件中提取音频

        Args:
            video_file: 视频文件路径
            output_dir: 输出目录（默认与视频文件同目录）
            show_progress: 是否显示进度提示

        Returns:
            音频文件路径
        """
        pass

    async def download_and_extract_audio(
        self,
        source: str,
        output_dir: str,
        show_progress: bool = True
    ) -> tuple[str, str, str]:
        """下载视频并提取音频（组合函数，默认实现）

        Args:
            source: 视频来源
            output_dir: 输出目录
            show_progress: 是否显示进度提示

        Returns:
            (audio_file, video_title, video_id) - 音频文件路径、视频标题、视频ID
        """
        # 下载视频
        video_file, video_title, video_id = await self.download_video(
            source, output_dir, show_progress
        )

        # 提取音频
        audio_file = self.extract_audio(video_file, output_dir, show_progress)

        return audio_file, video_title, video_id
