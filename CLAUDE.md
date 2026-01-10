# CLAUDE.md

本文件为 Claude Code 提供项目指导。

## 项目概述

**Bilibili-Captions** - B站字幕下载工具

- 从 B站 API 直接获取字幕
- 无字幕时使用 Whisper ASR 自动生成
- 自动繁简转换
- 提供 CLI 和 MCP 两种使用方式

**Python 版本要求：** >=3.10

## 项目结构

```
src/bilibili_captions/
├── core.py      # 核心功能（API 调用、ASR、繁简转换）
├── cli.py       # CLI 入口
└── server.py    # MCP 服务器
```

## 常用命令

```bash
# 安装依赖
uv sync

# 运行 CLI
uv run bilibili-captions <URL>

# 运行 MCP 服务器
uv run bilibili-captions-mcp

# 运行测试
uv run python tests/test_videos.py
```

## 核心模块 (core.py)

| 函数 | 说明 |
|------|------|
| `get_video_info(url)` | 获取视频信息 |
| `download_subtitle_content(url, format)` | API 下载字幕 |
| `transcribe_with_asr(audio_file, model_size)` | Whisper 转录 |
| `download_subtitles_with_asr(url, format, model_size)` | API 优先，ASR 兜底 |
| `convert_to_simplified(text)` | 繁体转简体 |

## 外部依赖

- **yt-dlp**: 下载 B站视频
- **ffmpeg**: 提取音频
- **faster-whisper**: ASR 语音识别（推荐）
- **openai-whisper**: ASR 备选方案

## 测试视频

| 视频 | 用途 |
|------|------|
| BV16YC3BrEDz | 有 API 字幕 |
| BV1qViQBwELr | 无字幕（测试 ASR 兜底） |
