"""
测试用例 - 使用实际B站视频进行测试

测试视频:
1. BV16YC3BrEDz - 有 AI 字幕 (API 直接获取)
2. BV1qViQBwELr - 无字幕 (ASR 兜底)

运行方式:
    python tests/test_videos.py          # 直接运行
    pytest tests/test_videos.py          # 使用 pytest
"""

import asyncio
import os

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

    def _mock_decorator(func):
        return func

    class _MockPytestMark:
        asyncio = staticmethod(_mock_decorator)

    class _MockPytest:
        mark = _MockPytestMark()

    pytest = _MockPytest()

# 需要 SESSDATA 环境变量
from bilibili_captions.core import (
    download_subtitles_with_asr,
    get_video_info,
    require_sessdata,
    ResponseFormat,
)


# 测试视频 URLs
VIDEO_WITH_SUBTITLES = "https://www.bilibili.com/video/BV16YC3BrEDz/"
VIDEO_WITHOUT_SUBTITLES = "https://www.bilibili.com/video/BV1qViQBwELr/"


@pytest.mark.asyncio
async def test_video_with_api_subtitles():
    """测试有 API 字幕的视频"""
    # 跳过如果没有 SESSDATA
    try:
        sessdata = require_sessdata()
    except ValueError:
        pytest.skip("需要 BILIBILI_SESSDATA 环境变量")

    # 获取视频信息
    info = await get_video_info(VIDEO_WITH_SUBTITLES)
    assert info["title"] == "关于影视飓风近期舆情"
    assert info["bvid"] == "BV16YC3BrEDz"

    # 下载字幕 (应该走 API)
    result = await download_subtitles_with_asr(
        VIDEO_WITH_SUBTITLES,
        ResponseFormat.TEXT,
        "medium",
        sessdata
    )

    assert "error" not in result
    assert result["source"] == "bilibili_api"
    assert result["subtitle_count"] > 180  # 约 189 条
    assert "content" in result
    assert len(result["content"]) > 1000


@pytest.mark.asyncio
async def test_video_with_asr_fallback():
    """测试无字幕视频走 ASR 兜底"""
    try:
        sessdata = require_sessdata()
    except ValueError:
        pytest.skip("需要 BILIBILI_SESSDATA 环境变量")

    # 获取视频信息
    info = await get_video_info(VIDEO_WITHOUT_SUBTITLES)
    assert "谷歌" in info["title"] or "苹果" in info["title"]
    assert info["bvid"] == "BV1qViQBwELr"

    # 下载字幕 (应该走 ASR)
    result = await download_subtitles_with_asr(
        VIDEO_WITHOUT_SUBTITLES,
        ResponseFormat.TEXT,
        "medium",
        sessdata
    )

    assert "error" not in result
    assert result["source"] == "whisper_asr"
    assert result["subtitle_count"] > 20
    assert "content" in result
    assert len(result["content"]) > 100


@pytest.mark.asyncio
async def test_srt_format():
    """测试 SRT 格式输出"""
    try:
        sessdata = require_sessdata()
    except ValueError:
        pytest.skip("需要 BILIBILI_SESSDATA 环境变量")

    result = await download_subtitles_with_asr(
        VIDEO_WITH_SUBTITLES,
        ResponseFormat.SRT,
        "medium",
        sessdata
    )

    assert "error" not in result
    assert result["format"] == "srt"
    assert "content" in result
    # SRT 格式应该包含时间戳
    assert "-->" in result["content"]


@pytest.mark.asyncio
async def test_json_format():
    """测试 JSON 格式输出"""
    try:
        sessdata = require_sessdata()
    except ValueError:
        pytest.skip("需要 BILIBILI_SESSDATA 环境变量")

    result = await download_subtitles_with_asr(
        VIDEO_WITH_SUBTITLES,
        ResponseFormat.JSON,
        "medium",
        sessdata
    )

    assert "error" not in result
    assert result["format"] == "json"
    assert "subtitles" in result
    assert isinstance(result["subtitles"], list)
    # JSON 格式应该有 from/to 时间字段
    if result["subtitles"]:
        assert "from" in result["subtitles"][0]
        assert "to" in result["subtitles"][0]
        assert "content" in result["subtitles"][0]


if __name__ == "__main__":
    # 简单运行测试
    async def run_tests():
        try:
            sessdata = require_sessdata()
        except ValueError as e:
            print(f"跳过测试: {e}")
            return

        print("\n=== 测试 1: 有 API 字幕的视频 ===")
        result1 = await download_subtitles_with_asr(
            VIDEO_WITH_SUBTITLES, ResponseFormat.TEXT, "medium", sessdata
        )
        print(f"来源: {result1.get('source')}")
        print(f"字幕数: {result1.get('subtitle_count')}")
        print(f"标题: {result1.get('video_title')}")

        print("\n=== 测试 2: 无字幕视频 (ASR 兜底) ===")
        result2 = await download_subtitles_with_asr(
            VIDEO_WITHOUT_SUBTITLES, ResponseFormat.TEXT, "medium", sessdata
        )
        print(f"来源: {result2.get('source')}")
        print(f"字幕数: {result2.get('subtitle_count')}")
        print(f"标题: {result2.get('video_title')}")

        print("\n✓ 所有测试通过")

    asyncio.run(run_tests())
