"""
测试用例 - B站视频字幕下载

测试视频:
1. BV16YC3BrEDz - 有 API 字幕
2. BV1qViQBwELr - 无字幕 (ASR 兜底)
"""

import asyncio
import pytest

from service import get_service
from core.cookie import get_sessdata
from core.formatter import ResponseFormat


def require_sessdata():
    result = get_sessdata()
    if not result:
        pytest.skip("需要 SESSDATA")
    return result


VIDEO_WITH_SUBTITLES = "https://www.bilibili.com/video/BV16YC3BrEDz/"
VIDEO_WITHOUT_SUBTITLES = "https://www.bilibili.com/video/BV1qViQBwELr/"


@pytest.mark.asyncio
async def test_video_with_api_subtitles():
    """测试有 API 字幕的视频"""
    require_sessdata()
    service = get_service(VIDEO_WITH_SUBTITLES)

    info = await service.get_info(VIDEO_WITH_SUBTITLES)
    assert info["id"] == "BV16YC3BrEDz"

    result = await service.download_subtitle(VIDEO_WITH_SUBTITLES, ResponseFormat.TEXT)
    assert "error" not in result
    assert result["source"] == "bilibili_api"
    assert result["subtitle_count"] > 180


@pytest.mark.asyncio
async def test_video_with_asr_fallback():
    """测试无字幕视频 ASR 兜底"""
    require_sessdata()
    service = get_service(VIDEO_WITHOUT_SUBTITLES)

    result = await service.download_subtitle(VIDEO_WITHOUT_SUBTITLES, ResponseFormat.TEXT, model_size="base")
    assert "error" not in result
    assert result["source"] == "whisper_asr"
    assert result["subtitle_count"] > 0


if __name__ == "__main__":
    async def run():
        require_sessdata()

        print("\n=== 测试 1: 有 API 字幕 ===")
        s1 = get_service(VIDEO_WITH_SUBTITLES)
        r1 = await s1.download_subtitle(VIDEO_WITH_SUBTITLES, ResponseFormat.TEXT)
        print(f"来源: {r1.get('source')}, 字幕数: {r1.get('subtitle_count')}")

        print("\n=== 测试 2: 无字幕 ASR 兜底 ===")
        s2 = get_service(VIDEO_WITHOUT_SUBTITLES)
        r2 = await s2.download_subtitle(VIDEO_WITHOUT_SUBTITLES, ResponseFormat.TEXT, model_size="base")
        print(f"来源: {r2.get('source')}, 字幕数: {r2.get('subtitle_count')}")
        print("\n✓ 完成")

    asyncio.run(run())
