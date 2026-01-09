# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

B站字幕抓取工具 - 一个Python脚本，用于从B站视频下载字幕。如果视频没有自带字幕，会使用Whisper ASR自动生成。

## 常用命令

```bash
# 安装依赖
python -m pip install -e .

# 或使用 uv (如果已安装)
uv sync

# 运行程序
python main.py <B站视频URL>

# 示例
python main.py https://www.bilibili.com/video/BV1xx411c7mD/
```

## 外部依赖

程序依赖以下外部工具，需单独安装：
- **yt-dlp**: 用于下载B站视频 (`pip install yt-dlp` 或系统包管理器)
- **ffmpeg**: 用于从视频中提取音频 (系统包管理器安装)

## 代码架构

### 核心流程 (`main.py`)

1. `get_video_info(url)` - 获取视频标题、CID和BV号
2. `get_subtitles_from_bilibili()` - 尝试从B站API下载现有字幕
3. `generate_subtitles_with_asr()` - 如无字幕，使用Whisper生成

### 字幕格式

- 输出格式为 **SRT** 格式
- 下载的字幕保存为 `{视频标题}.srt`
- ASR生成的字幕保存为 `{视频标题}_asr.srt`
- ASR生成的字幕会**自动转换为简体中文**（使用 opencc）

### B站API使用

- 视频信息: `https://api.bilibili.com/x/web-interface/view?bvid={bvid}`
- 字幕列表: `https://api.bilibili.com/x/player/v2?cid={cid}&bvid={bvid}`
- 字幕内容: 从 `subtitle_url` 获取JSON格式，需转换为SRT

### 时间格式转换

B站API使用秒数（浮点），SRT格式需要 `HH:MM:SS,mmm` 格式。
