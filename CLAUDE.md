# CLAUDE.md

本文件为 Claude Code 提供项目指导。

## 项目概述

**Bilibili-Captions** - B站字幕下载工具

- 从 B站 API 直接获取字幕
- 无字幕时使用 Whisper ASR 自动生成
- 自动繁简转换
- 提供 CLI 和 MCP 两种使用方式
- **支持自动从浏览器读取 SESSDATA**（Chrome、Edge、Firefox、Brave）

**Python 版本要求：** >=3.10

## 项目结构

```
src/bilibili_captions/
├── core.py      # 核心功能（API 调用、ASR、繁简转换、SESSDATA 管理）
├── cli.py       # CLI 入口
├── server.py    # MCP 服务器
└── browser.py   # 浏览器 Cookie 读取模块
```

## 常用命令

```bash
# 安装依赖
uv sync

# 运行 CLI（默认自动从浏览器读取 SESSDATA）
uv run bilibili-captions <URL>

# 指定浏览器（可选）
uv run bilibili-captions --browser chrome <URL>

# 运行 MCP 服务器
uv run bilibili-captions-mcp

# 运行测试
uv run python tests/test_videos.py
```

## 核心模块 (core.py)

| 函数 | 说明 |
|------|------|
| `get_video_info(url)` | 获取视频信息 |
| `list_subtitles(url)` | 列出可用字幕 |
| `download_subtitle_content(url, format)` | API 下载字幕 |
| `download_and_extract_audio(url, output_dir)` | 下载视频并提取音频 |
| `transcribe_with_asr(audio_file, model_size)` | Whisper 转录 |
| `download_subtitles_with_asr(url, format, model_size)` | API 优先，ASR 兜底 |
| `convert_to_simplified(text)` | 繁体转简体 |
| `get_sessdata(sessdata, browser)` | 获取 SESSDATA（默认浏览器="auto"） |
| `require_sessdata(sessdata, browser)` | 必需 SESSDATA，否则抛出异常 |

## 浏览器模块 (browser.py)

| 函数 | 说明 |
|------|------|
| `get_sessdata_from_browser(browser)` | 从浏览器读取 SESSDATA |
| `list_available_browsers()` | 列出可用浏览器 |

**支持的浏览器：** `auto` (自动检测) / `chrome` / `edge` / `firefox` / `brave`

## 外部依赖

- **yt-dlp**: 下载 B站视频
- **ffmpeg**: 提取音频
- **mlx-whisper**: ASR 语音识别（Apple Silicon 优化）
- **browser-cookie3**: 从浏览器读取加密 Cookie（Chrome、Edge、Firefox、Brave）

## 测试视频

| 视频 | 用途 |
|------|------|
| BV16YC3BrEDz | 有 API 字幕 |
| BV1qViQBwELr | 无字幕（测试 ASR 兜底） |
