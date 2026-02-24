# CLAUDE.md

本文件为 Claude Code 提供项目指导。

## 项目概述

**Video-Captions** - 视频字幕下载工具

- 支持 B站、YouTube 和本地文件
- 从 API 直接获取字幕
- 无字幕时使用 Whisper ASR 自动生成
- 自动繁简转换
- 提供 CLI 和 MCP 两种使用方式
- 支持自动从浏览器读取 Cookie（Chrome、Edge、Firefox、Brave）

**Python 版本要求：** >=3.10

## 项目结构

```
src/
├── core/                    # 基础层：通用功能
│   ├── asr.py              # ASR 转录
│   ├── audio.py            # 音频提取
│   ├── browser.py          # 浏览器 Cookie
│   ├── cookie.py           # Cookie 管理
│   ├── formatter.py        # 字幕格式化
│   ├── logging.py          # 日志系统
│   └── text.py             # 文本处理
├── handler/                 # 接入层：CLI 和 MCP
│   ├── cli.py              # CLI 入口
│   ├── mcp.py              # MCP 服务器
│   └── base.py             # 共享功能
└── service/                 # 业务层：平台服务
    ├── base.py             # 抽象基类
    ├── bilibili.py         # B站服务
    ├── youtube.py          # YouTube 服务
    └── local.py            # 本地文件服务
```

## 常用命令

```bash
# 安装依赖
uv sync

# 运行 CLI
uv run video-captions <URL>

# 指定浏览器读取 Cookie
uv run video-captions --browser chrome <URL>

# 指定输出格式
uv run video-captions --format srt <URL>

# 指定 ASR 模型
uv run video-captions --model small <URL>

# 显示详细日志
uv run video-captions --verbose <URL>

# 运行 MCP 服务器
uv run video-captions-mcp

# 运行测试
uv run python tests/test_bilibili.py
uv run python tests/test_youtube.py
```

## CLI 选项

| 选项 | 说明 |
|------|------|
| `--browser` | 从浏览器读取 Cookie: `auto` / `chrome` / `edge` / `firefox` / `brave` |
| `--model` | ASR 模型: `base` / `small` / `medium` / `large` |
| `--format` | 输出格式: `text` / `srt` / `json` |
| `--verbose, -v` | 显示详细日志 |

## 外部依赖

- **yt-dlp**: 下载视频
- **ffmpeg**: 提取音频
- **mlx-whisper**: ASR 语音识别（Apple Silicon 优化）
- **browser-cookie3**: 从浏览器读取加密 Cookie

## 测试视频

| 视频 | 平台 | 用途 |
|------|------|------|
| BV16YC3BrEDz | B站 | 有 API 字幕 |
| BV1qViQBwELr | B站 | 无字幕（测试 ASR 兜底） |
| kQ-aFczITCg | YouTube | 有 API 字幕 |
| 5GJU5-UMNWk | YouTube | 无字幕（测试 ASR 兜底） |
