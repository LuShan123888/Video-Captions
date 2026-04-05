"""
ASR 语音识别 - 使用 mlx-whisper 进行语音转录
"""

import os
import time
from typing import Dict, Any, List

from .logging import log_step, _verbose_log

# 禁用 tqdm 进度条，避免非 verbose 模式下 huggingface_hub 输出无关信息
os.environ["TQDM_DISABLE"] = "1"

# 模型映射
MODEL_MAP = {
    "base": "mlx-community/whisper-base-mlx",
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large": "mlx-community/whisper-large-v3-mlx",
}


def _suppress_output(func, *args, **kwargs):
    """在函数执行期间抑制所有 stdout/stderr 输出（包括 C 扩展级别的写入）"""
    devnull = os.open(os.devnull, os.O_WRONLY)
    # 保存原始 fd
    stdout_fd = os.dup(1)
    stderr_fd = os.dup(2)
    try:
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        return func(*args, **kwargs)
    finally:
        # 恢复原始 fd
        os.dup2(stdout_fd, 1)
        os.dup2(stderr_fd, 2)
        os.close(devnull)
        os.close(stdout_fd)
        os.close(stderr_fd)


async def transcribe_with_asr(
    audio_file: str,
    model_size: str = "large",
    show_progress: bool = True
) -> Dict[str, Any]:
    """使用 Whisper ASR 生成字幕

    Args:
        audio_file: 音频文件路径
        model_size: 模型大小 (base/small/medium/large)
        show_progress: 是否显示进度

    Returns:
        {
            "source": "whisper_asr",
            "segments": [{"start": 0.0, "end": 1.0, "text": "..."}],
            "text": "完整文本",
            "language": "zh",
            "duration": 12.5
        }
    """
    import mlx_whisper

    model_path = MODEL_MAP.get(model_size, MODEL_MAP["large"])

    if show_progress:
        log_step(f"加载 Whisper {model_size} 模型", "(mlx-whisper)")

    start_time = time.time()

    # 非 verbose 模式下抑制 mlx_whisper 及 huggingface_hub 的所有输出
    if _verbose_log:
        result = mlx_whisper.transcribe(
            audio_file,
            path_or_hf_repo=model_path,
            language="zh",
            hallucination_silence_threshold=0.5,
            condition_on_previous_text=False,
        )
    else:
        result = _suppress_output(mlx_whisper.transcribe,
            audio_file,
            path_or_hf_repo=model_path,
            language="zh",
            hallucination_silence_threshold=0.5,
            condition_on_previous_text=False,
        )

    elapsed = time.time() - start_time

    segments = result.get("segments", [])
    segment_list: List[Dict[str, Any]] = []
    text_lines: List[str] = []

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
