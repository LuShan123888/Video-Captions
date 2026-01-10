# Bilibili-Captions

[简体中文](#简体中文) | [English](#english)

---

## 简体中文

B站字幕下载工具，支持 API 获取和 Whisper ASR 自动生成。

### 功能特性

- 🎬 **API 下载** - 直接从 B站 API 获取视频字幕
- 🤖 **ASR 生成** - 无字幕时自动使用 Whisper 生成
- 🌏 **繁简转换** - 自动转换为简体中文
- 📦 **MCP 服务器** - 集成到 Claude Desktop
- 🧪 **完整测试** - 包含真实视频测试用例

## 使用

### 安装

**系统要求：** Python >=3.10

```bash
# 使用 uv tool 安装（推荐）
uv tool install bilibili-captions

# 或使用 pip
pip install bilibili-captions
```

### 运行

```bash
# 1. 设置 SESSDATA 环境变量
export BILIBILI_SESSDATA="你的值"

# 2. 运行命令
bilibili-captions <BV号或URL> [模型大小]

# 示例 - 支持多种 URL 格式
bilibili-captions BV16YC3BrEDz                                    # 直接 BV 号
bilibili-captions https://www.bilibili.com/video/BV1qViQBwELr   # 完整 URL
bilibili-captions https://www.bilibili.com/list/watchlater/?bvid=BV16HqFBZE6N  # 稍后观看
bilibili-captions "【我们拍到了，中国自己的可回收火箭。】 https://www.bilibili.com/video/BV1y7qwBuEBw/?share_source=copy_web&vd_source=17128cd8d40d0802659ba5ee37ab47d1"  # 分享复制
```

**模型大小选项：**
- `base` - 最快，精度较低
- `small` - 较快
- `medium` - 平衡（默认）
- `large` - 最慢，精度最高

### MCP 服务器

在 Claude Desktop 的 `claude_desktop_config.json` 中配置：

```json
{
  "mcpServers": {
    "bilibili-captions": {
      "command": "uvx",
      "args": ["bilibili-captions-mcp"],
      "env": {
        "BILIBILI_SESSDATA": "你的 SESSDATA"
      },
      "timeout": 600000
    }
  }
}
```

### MCP 工具

#### download_captions

下载 B 站视频字幕，支持多种格式。

| 参数 | 类型 | 说明 |
|------|------|------|
| `url` | 必需 | B站视频URL或BV号 |
| `format` | 可选 | `text`(默认) / `srt` / `json` |
| `model_size` | 可选 | `base` / `small` / `medium`(默认) / `large` |

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

## 开发

### 项目结构

```
Bilibili-Captions/
├── src/bilibili_captions/
│   ├── __init__.py
│   ├── core.py      # 核心 API 功能
│   ├── cli.py       # CLI 入口
│   └── server.py    # MCP 服务器
├── tests/
│   ├── __init__.py
│   └── test_videos.py    # 测试用例
├── .env.example          # 配置示例
├── pyproject.toml
└── README.md
```

### 本地运行

```bash
# 克隆项目
git clone https://github.com/LuShan123888/Bilibili-Captions.git
cd Bilibili-Captions

# 安装依赖
uv sync

# 设置 SESSDATA
cp .env.example .env
# 编辑 .env 填入 SESSDATA
```

#### CLI 运行

```bash
# 方式1: uv run（推荐开发环境）
uv run bilibili-captions BV16YC3BrEDz
uv run bilibili-captions https://www.bilibili.com/video/BV1qViQBwELr small

# 方式2: 直接调用模块
uv run python -m bilibili_captions.cli <URL>

# 方式3: 安装后全局使用
uv tool install -e .
bilibili-captions <URL>
```

#### MCP 服务器

在 Claude Desktop 的 `claude_desktop_config.json` 中添加本地开发配置：

```json
{
  "mcpServers": {
    "bilibili-captions-dev": {
      "command": "uv",
      "args": ["--directory", "/Users/cian/Code/Bilibili-Captions", "run", "bilibili-captions-mcp"],
      "env": {
        "BILIBILI_SESSDATA": "你的 SESSDATA"
      },
      "timeout": 600000
    }
  }
}
```

### 测试

项目包含两个真实视频的测试用例：

| 视频 | 场景 | 预期结果 |
|------|------|---------|
| BV16YC3BrEDz | 有 API 字幕 | 189 条，来源 `bilibili_api` |
| BV1qViQBwELr | 无字幕 ASR | 30 条，来源 `whisper_asr` |

```bash
uv run python tests/test_videos.py
# 或
pytest tests/test_videos.py
```

## 配置

### SESSDATA 获取

1. 登录 [B站](https://www.bilibili.com/)
2. F12 → Application → Cookies → `SESSDATA`
3. 复制值到环境变量或 `.env` 文件

```bash
# 方式1: 环境变量
export BILIBILI_SESSDATA="你的值"

# 方式2: .env 文件
cp .env.example .env
# 编辑 .env 填入 SESSDATA
```

## 依赖

### Python 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `mcp` | >=1.0.0 | MCP 协议支持 |
| `httpx` | >=0.28.1 | HTTP 客户端 |
| `requests` | >=2.32.5 | HTTP 请求 |
| `faster-whisper` | >=1.0.0 | 语音识别（推荐） |
| `openai-whisper` | - | 语音识别备选 |
| `opencc-python-reimplemented` | >=0.1.7 | 繁简转换 |
| `filelock` | >=3.20.0 | 文件锁定 |

### 系统依赖

```bash
# macOS
brew install yt-dlp ffmpeg

# Linux
apt install yt-dlp ffmpeg
```

## 许可证

MIT

---

## English

A Bilibili subtitle download tool that supports API fetching and Whisper ASR generation.

### Features

- 🎬 **API Download** - Fetch video subtitles directly from Bilibili API
- 🤖 **ASR Generation** - Automatically generate subtitles with Whisper when none exist
- 🌏 **Conversion** - Automatically convert Traditional Chinese to Simplified Chinese
- 📦 **MCP Server** - Integrate with Claude Desktop
- 🧪 **Tested** - Includes real video test cases

## Usage

### Installation

**System Requirement:** Python >=3.10

```bash
# Install using uv tool (recommended)
uv tool install bilibili-captions

# Or using pip
pip install bilibili-captions
```

### Running

```bash
# 1. Set SESSDATA environment variable
export BILIBILI_SESSDATA="your_value"

# 2. Run command
bilibili-captions <BV_ID_or_URL> [model_size]

# Examples - supports multiple URL formats
bilibili-captions BV16YC3BrEDz                                    # Direct BV ID
bilibili-captions https://www.bilibili.com/video/BV1qViQBwELr   # Full URL
bilibili-captions https://www.bilibili.com/list/watchlater/?bvid=BV16HqFBZE6N  # Watch later
bilibili-captions "【Title】 https://www.bilibili.com/video/BV1y7qwBuEBw/?share_source=copy_web&vd_source=xxx"  # Share copy
```

**Model size options:**
- `base` - Fastest, lower accuracy
- `small` - Faster
- `medium` - Balanced (default)
- `large` - Slowest, highest accuracy

### MCP Server

Configure in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bilibili-captions": {
      "command": "uvx",
      "args": ["bilibili-captions-mcp"],
      "env": {
        "BILIBILI_SESSDATA": "your_SESSDATA"
      },
      "timeout": 600000
    }
  }
}
```

### MCP Tools

#### download_captions

Download Bilibili video subtitles in multiple formats.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | Required | Bilibili video URL or BV ID |
| `format` | Optional | `text`(default) / `srt` / `json` |
| `model_size` | Optional | `base` / `small` / `medium`(default) / `large` |

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

## Development

### Project Structure

```
Bilibili-Captions/
├── src/bilibili_captions/
│   ├── __init__.py
│   ├── core.py      # Core API functionality
│   ├── cli.py       # CLI entry point
│   └── server.py    # MCP server
├── tests/
│   ├── __init__.py
│   └── test_videos.py    # Test cases
├── .env.example          # Configuration example
├── pyproject.toml
└── README.md
```

### Local Development

```bash
# Clone repository
git clone https://github.com/LuShan123888/Bilibili-Captions.git
cd Bilibili-Captions

# Install dependencies
uv sync

# Set SESSDATA
cp .env.example .env
# Edit .env and fill in SESSDATA
```

#### CLI

```bash
# Method 1: uv run (recommended for development)
uv run bilibili-captions BV16YC3BrEDz
uv run bilibili-captions https://www.bilibili.com/video/BV1qViQBwELr small

# Method 2: Direct module call
uv run python -m bilibili_captions.cli <URL>

# Method 3: Global use after installation
uv tool install -e .
bilibili-captions <URL>
```

#### MCP Server (Development)

Add local development config in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bilibili-captions-dev": {
      "command": "uv",
      "args": ["--directory", "/path/to/Bilibili-Captions", "run", "bilibili-captions-mcp"],
      "env": {
        "BILIBILI_SESSDATA": "your_SESSDATA"
      },
      "timeout": 600000
    }
  }
}
```

### Testing

The project includes test cases for two real videos:

| Video | Scenario | Expected Result |
|-------|----------|-----------------|
| BV16YC3BrEDz | Has API subtitles | 189 entries, source `bilibili_api` |
| BV1qViQBwELr | No subtitles ASR | 30 entries, source `whisper_asr` |

```bash
uv run python tests/test_videos.py
# or
pytest tests/test_videos.py
```

## Configuration

### Get SESSDATA

1. Login to [Bilibili](https://www.bilibili.com/)
2. F12 → Application → Cookies → `SESSDATA`
3. Copy value to environment variable or `.env` file

```bash
# Method 1: Environment variable
export BILIBILI_SESSDATA="your_value"

# Method 2: .env file
cp .env.example .env
# Edit .env and fill in SESSDATA
```

## Dependencies

### Python Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `mcp` | >=1.0.0 | MCP protocol support |
| `httpx` | >=0.28.1 | HTTP client |
| `requests` | >=2.32.5 | HTTP requests |
| `faster-whisper` | >=1.0.0 | Speech recognition (recommended) |
| `openai-whisper` | - | Speech recognition alternative |
| `opencc-python-reimplemented` | >=0.1.7 | Traditional/Simplified conversion |
| `filelock` | >=3.20.0 | File locking |

### System Dependencies

```bash
# macOS
brew install yt-dlp ffmpeg

# Linux
apt install yt-dlp ffmpeg
```

## License

MIT
