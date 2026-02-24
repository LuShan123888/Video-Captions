"""
音频处理 - 从视频文件提取音频
"""

import os
import subprocess
from typing import Optional

from .logging import log_step


def is_video_file(file_path: str) -> bool:
    """判断文件是否为视频格式"""
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg'}
    return os.path.splitext(file_path)[1].lower() in video_extensions


def is_audio_file(file_path: str) -> bool:
    """判断文件是否为音频格式"""
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma', '.opus'}
    return os.path.splitext(file_path)[1].lower() in audio_extensions


def extract_audio(
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

    Raises:
        subprocess.CalledProcessError: ffmpeg 提取失败
    """
    if output_dir is None:
        output_dir = os.path.dirname(video_file) or "."

    base_name = os.path.splitext(os.path.basename(video_file))[0]
    audio_filename = os.path.join(output_dir, f"{base_name}.wav")

    # 如果音频已存在，直接返回
    if os.path.exists(audio_filename):
        return audio_filename

    os.makedirs(output_dir, exist_ok=True)

    # 使用 ffmpeg 提取音频
    if show_progress:
        log_step("正在提取音频")

    result = subprocess.run(
        ['ffmpeg', '-y', '-i', video_file, '-vn',
         '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_filename],
        capture_output=True
    )

    if result.returncode != 0:
        # 检查视频文件是否存在
        if not os.path.exists(video_file):
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                f"视频文件不存在: {video_file}"
            )

        file_size = os.path.getsize(video_file)
        if file_size == 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                f"视频文件大小为 0: {video_file}"
            )

        stderr = result.stderr.decode('utf-8', errors='ignore')
        error_msg = f"ffmpeg 提取音频失败 (退出码: {result.returncode})\n"
        error_msg += f"视频文件: {video_file} (大小: {file_size} bytes)\n"
        if stderr:
            error_msg += f"ffmpeg 错误: {stderr[:500]}"
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            error_msg
        )

    return audio_filename
