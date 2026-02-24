"""
ASR 语音识别 - 使用 mlx-whisper 进行语音转录
"""

import time
from typing import Dict, Any, List

from .logging import log_step

# 模型映射
MODEL_MAP = {
    "base": "mlx-community/whisper-base-mlx",
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large": "mlx-community/whisper-large-v3-mlx",
}


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

    result = mlx_whisper.transcribe(
        audio_file,
        path_or_hf_repo=model_path,
        language="zh",
        hallucination_silence_threshold=0.5,
        condition_on_previous_text=False,
        verbose=show_progress,
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
