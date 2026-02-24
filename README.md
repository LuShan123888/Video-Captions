# Video-Captions

[简体中文](#简体中文) | [English](#english)

---

## 简体中文

视频字幕下载工具，支持 B站、YouTube 和本地文件，API 获取和 Whisper ASR 自动生成。

### 功能特性

- 🎬 **多平台支持** - B站、YouTube、本地音视频文件
- 🤖 **ASR 生成** - 无字幕时自动使用 Whisper 生成
- 🌏 **繁简转换** - 自动转换为简体中文
- 📦 **MCP 服务器** - 集成到 Claude Desktop
- 🧪 **完整测试** - 包含真实视频测试用例

## 使用

### 安装

**系统要求：** Python >=3.10

```bash
# 使用 uv tool 安装（推荐）
uv tool install video-captions

# 或使用 pip
pip install video-captions

# 旧命令名仍然可用（向后兼容）
uv tool install video-captions
```

### 运行

```bash
# B站视频（默认自动从浏览器读取 Cookie）
video-captions https://www.bilibili.com/video/BV16YC3BrEDz

# YouTube 视频
video-captions https://www.youtube.com/watch?v=kQ-aFczITCg

# 本地音视频文件
video-captions /path/to/video.mp4
video-captions /path/to/audio.mp3

# 指定浏览器读取 Cookie（可选）
video-captions --browser chrome <URL>

# 指定输出格式
video-captions --format srt <URL>      # SRT 字幕格式
video-captions --format json <URL>     # JSON 结构化数据

# 仅查看视频信息
video-captions --info <URL>

# 仅列出可用字幕
video-captions --list <URL>

# 显示详细日志
video-captions --verbose <URL>
```

**命令行选项：**
| 选项 | 说明 |
|------|------|
| `--browser` | 从浏览器读取 Cookie: `auto`(默认) / `chrome` / `edge` / `firefox` / `brave` |
| `--model` | ASR 模型: `base` / `small` / `medium` / `large`(默认) |
| `--format` | 输出格式: `text`(默认) / `srt` / `json` |
| `--info` | 仅显示视频信息 |
| `--list` | 仅列出可用字幕 |
| `--verbose, -v` | 显示详细日志 |

**模型大小选项：**
- `base` - 最快，精度较低
- `small` - 较快
- `medium` - 平衡
- `large` - 精度最高（默认，mlx-whisper 优化）

### MCP 服务器

在 Claude Desktop 的 `claude_desktop_config.json` 中配置：

```json
{
  "mcpServers": {
    "video-captions": {
      "command": "uvx",
      "args": ["video-captions-mcp"],
      "timeout": 600000
    }
  }
}
```

> **注意：** B站视频会自动从浏览器读取 Cookie，无需手动配置 SESSDATA。

### MCP 工具

#### download_captions

下载视频字幕，支持 B站、YouTube 和本地文件。

| 参数 | 类型 | 说明 |
|------|------|------|
| `url` | 必需 | 视频 URL 或本地文件路径 |
| `format` | 可选 | `text`(默认) / `srt` / `json` |
| `model_size` | 可选 | `base` / `small` / `medium` / `large`(默认) |
| `browser` | 可选 | `auto`(默认) / `chrome` / `edge` / `firefox` / `brave` |

**返回示例：**
```json
{
  "source": "bilibili_api",
  "format": "text",
  "subtitle_count": 189,
  "content": "字幕内容...",
  "video_title": "视频标题"
}
```

#### transcribe_local_file

对本地音频/视频文件进行 ASR 语音识别。

| 参数 | 类型 | 说明 |
|------|------|------|
| `file_path` | 必需 | 本地文件路径 |
| `format` | 可选 | `text`(默认) / `srt` / `json` |
| `model_size` | 可选 | `base` / `small` / `medium` / `large`(默认) |

## 开发

### 项目结构

```
video-captions/
├── src/bilibili_captions/
│   ├── handler/           # 接入层：CLI 和 MCP
│   │   ├── cli.py         # CLI 入口
│   │   ├── mcp.py         # MCP 服务器
│   │   └── base.py        # 共享功能
│   ├── service/           # 业务层：平台服务
│   │   ├── base.py        # 抽象基类
│   │   ├── bilibili.py    # B站服务
│   │   ├── youtube.py     # YouTube 服务
│   │   └── local.py       # 本地文件服务
│   ├── core/              # 基础层：通用功能
│   │   ├── asr.py         # ASR 转录
│   │   ├── audio.py       # 音频提取
│   │   ├── cookie.py      # Cookie 管理
│   │   ├── formatter.py   # 字幕格式化
│   │   ├── logging.py     # 日志系统
│   │   └── text.py        # 文本处理
│   └── __init__.py
├── tests/
│   ├── test_bilibili.py   # B站测试用例
│   └── test_youtube.py    # YouTube 测试用例
├── pyproject.toml
└── README.md
```

### 本地运行

```bash
# 克隆项目
git clone https://github.com/LuShan123888/Video-Captions.git
cd Video-Captions

# 安装依赖
uv sync
```

#### CLI 运行

```bash
# 方式1: uv run（推荐开发环境）
uv run video-captions https://www.bilibili.com/video/BV16YC3BrEDz
uv run video-captions https://www.youtube.com/watch?v=kQ-aFczITCg

# 方式2: 安装后全局使用
uv tool install -e .
video-captions <URL>
```

#### MCP 服务器

在 Claude Desktop 的 `claude_desktop_config.json` 中添加本地开发配置：

```json
{
  "mcpServers": {
    "video-captions-dev": {
      "command": "uv",
      "args": ["--directory", "/path/to/Bilibili-Captions", "run", "video-captions-mcp"],
      "timeout": 600000
    }
  }
}
```

### 测试

项目包含真实视频的测试用例：

| 视频 | 平台 | 场景 |
|------|------|------|
| BV16YC3BrEDz | B站 | 有 API 字幕 |
| BV1qViQBwELr | B站 | 无字幕 ASR 兜底 |
| kQ-aFczITCg | YouTube | 有 API 字幕 |
| 5GJU5-UMNWk | YouTube | 无字幕 ASR 兜底 |

```bash
uv run python tests/test_bilibili.py
uv run python tests/test_youtube.py
# 或
pytest tests/
```

## 配置

### Cookie 获取

**B站（自动读取，推荐！）**

默认情况下，工具会自动从浏览器读取 SESSDATA，你只需要：

1. 在浏览器中登录 [B站](https://www.bilibili.com/)
2. 直接运行 `video-captions <视频链接>`

支持浏览器：Chrome、Edge、Firefox、Brave

**B站（环境变量，备选）**

1. 登录 [B站](https://www.bilibili.com/)
2. F12 → Application → Cookies → `SESSDATA`
3. 设置环境变量

```bash
export BILIBILI_SESSDATA="你的值"
```

**YouTube**

YouTube 视频通常不需要登录。对于年龄限制视频，工具会自动尝试从浏览器读取 Cookie。

## 依赖

### Python 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `mcp` | >=1.0.0 | MCP 协议支持 |
| `httpx` | >=0.28.1 | HTTP 客户端 |
| `mlx-whisper` | >=0.4.0 | 语音识别（Apple Silicon 优化） |
| `opencc-python-reimplemented` | >=0.1.7 | 繁简转换 |
| `browser-cookie3` | >=0.19.0 | 浏览器 Cookie 读取 |

> **注意：** ASR 功能使用 mlx-whisper，仅支持 Apple Silicon (M1/M2/M3/M4) Mac。

### 系统依赖

```bash
# macOS (Apple Silicon)
brew install yt-dlp ffmpeg
```

## 许可证

MIT

---

## English

A video subtitle download tool that supports Bilibili, YouTube, and local files with API fetching and Whisper ASR generation.

### Features

- 🎬 **Multi-Platform** - Bilibili, YouTube, and local audio/video files
- 🤖 **ASR Generation** - Automatically generate subtitles with Whisper when none exist
- 🌏 **Conversion** - Automatically convert Traditional Chinese to Simplified Chinese
- 📦 **MCP Server** - Integrate with Claude Desktop
- 🧪 **Tested** - Includes real video test cases

## Usage

### Installation

**System Requirement:** Python >=3.10

```bash
# Install using uv tool (recommended)
uv tool install video-captions

# Or using pip
pip install video-captions

# Old command names still work (backward compatible)
uv tool install video-captions
```

### Running

```bash
# Bilibili video (auto-read Cookie from browser)
video-captions https://www.bilibili.com/video/BV16YC3BrEDz

# YouTube video
video-captions https://www.youtube.com/watch?v=kQ-aFczITCg

# Local audio/video file
video-captions /path/to/video.mp4
video-captions /path/to/audio.mp3

# Specify browser for Cookie (optional)
video-captions --browser chrome <URL>

# Specify output format
video-captions --format srt <URL>      # SRT subtitle format
video-captions --format json <URL>     # JSON structured data

# View video info only
video-captions --info <URL>

# List available subtitles only
video-captions --list <URL>

# Show verbose logs
video-captions --verbose <URL>
```

**CLI Options:**
| Option | Description |
|--------|-------------|
| `--browser` | Read Cookie from browser: `auto`(default) / `chrome` / `edge` / `firefox` / `brave` |
| `--model` | ASR model: `base` / `small` / `medium` / `large`(default) |
| `--format` | Output format: `text`(default) / `srt` / `json` |
| `--info` | Show video info only |
| `--list` | List available subtitles only |
| `--verbose, -v` | Show verbose logs |

**Model size options:**
- `base` - Fastest, lower accuracy
- `small` - Faster
- `medium` - Balanced
- `large` - Highest accuracy (default, mlx-whisper optimized)

### MCP Server

Configure in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "video-captions": {
      "command": "uvx",
      "args": ["video-captions-mcp"],
      "timeout": 600000
    }
  }
}
```

> **Note:** For Bilibili videos, Cookie is automatically read from browser, no manual SESSDATA configuration needed.

### MCP Tools

#### download_captions

Download video subtitles, supports Bilibili, YouTube, and local files.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | Required | Video URL or local file path |
| `format` | Optional | `text`(default) / `srt` / `json` |
| `model_size` | Optional | `base` / `small` / `medium` / `large`(default) |
| `browser` | Optional | `auto`(default) / `chrome` / `edge` / `firefox` / `brave` |

**Response example:**
```json
{
  "source": "bilibili_api",
  "format": "text",
  "subtitle_count": 189,
  "content": "subtitle content...",
  "video_title": "video title"
}
```

#### transcribe_local_file

Perform ASR speech recognition on local audio/video files.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | Required | Local file path |
| `format` | Optional | `text`(default) / `srt` / `json` |
| `model_size` | Optional | `base` / `small` / `medium` / `large`(default) |

## Development

### Project Structure

```
video-captions/
├── src/bilibili_captions/
│   ├── handler/           # Handler layer: CLI and MCP
│   │   ├── cli.py         # CLI entry point
│   │   ├── mcp.py         # MCP server
│   │   └── base.py        # Shared functionality
│   ├── service/           # Service layer: platform services
│   │   ├── base.py        # Abstract base class
│   │   ├── bilibili.py    # Bilibili service
│   │   ├── youtube.py     # YouTube service
│   │   └── local.py       # Local file service
│   ├── core/              # Core layer: common utilities
│   │   ├── asr.py         # ASR transcription
│   │   ├── audio.py       # Audio extraction
│   │   ├── cookie.py      # Cookie management
│   │   ├── formatter.py   # Subtitle formatting
│   │   ├── logging.py     # Logging system
│   │   └── text.py        # Text processing
│   └── __init__.py
├── tests/
│   ├── test_bilibili.py   # Bilibili test cases
│   └── test_youtube.py    # YouTube test cases
├── pyproject.toml
└── README.md
```

### Local Development

```bash
# Clone repository
git clone https://github.com/LuShan123888/Video-Captions.git
cd Video-Captions

# Install dependencies
uv sync
```

#### CLI

```bash
# Method 1: uv run (recommended for development)
uv run video-captions https://www.bilibili.com/video/BV16YC3BrEDz
uv run video-captions https://www.youtube.com/watch?v=kQ-aFczITCg

# Method 2: Global use after installation
uv tool install -e .
video-captions <URL>
```

#### MCP Server (Development)

Add local development config in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "video-captions-dev": {
      "command": "uv",
      "args": ["--directory", "/path/to/Bilibili-Captions", "run", "video-captions-mcp"],
      "timeout": 600000
    }
  }
}
```

### Testing

The project includes test cases for real videos:

| Video | Platform | Scenario |
|-------|----------|----------|
| BV16YC3BrEDz | Bilibili | Has API subtitles |
| BV1qViQBwELr | Bilibili | No subtitles ASR fallback |
| kQ-aFczITCg | YouTube | Has API subtitles |
| 5GJU5-UMNWk | YouTube | No subtitles ASR fallback |

```bash
uv run python tests/test_videos.py
uv run python tests/test_youtube.py
# or
pytest tests/
```

## Configuration

### Cookie

**Bilibili (Auto-read, recommended!)**

By default, the tool automatically reads SESSDATA from your browser. You only need to:

1. Login to [Bilibili](https://www.bilibili.com/) in your browser
2. Run `video-captions <video_url>`

Supported browsers: Chrome, Edge, Firefox, Brave

**Bilibili (Environment variable, alternative)**

1. Login to [Bilibili](https://www.bilibili.com/)
2. F12 → Application → Cookies → `SESSDATA`
3. Set environment variable

```bash
export BILIBILI_SESSDATA="your_value"
```

**YouTube**

YouTube videos typically don't require login. For age-restricted videos, the tool automatically tries to read cookies from the browser.

## Dependencies

### Python Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `mcp` | >=1.0.0 | MCP protocol support |
| `httpx` | >=0.28.1 | HTTP client |
| `mlx-whisper` | >=0.4.0 | Speech recognition (Apple Silicon optimized) |
| `opencc-python-reimplemented` | >=0.1.7 | Traditional/Simplified conversion |
| `browser-cookie3` | >=0.19.0 | Browser cookie reading |

> **Note:** ASR uses mlx-whisper, which only supports Apple Silicon (M1/M2/M3/M4) Macs.

### System Dependencies

```bash
# macOS (Apple Silicon)
brew install yt-dlp ffmpeg
```

## License

MIT
