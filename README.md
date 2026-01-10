# bilibili-captions

B站字幕下载工具，支持 API 获取和 Whisper ASR 自动生成。

## 功能特性

- 🎬 **API 下载** - 直接从 B站 API 获取视频字幕
- 🤖 **ASR 生成** - 无字幕时自动使用 Whisper 生成
- 🌏 **繁简转换** - 自动转换为简体中文
- 📦 **MCP 服务器** - 集成到 Claude Desktop

## 安装

```bash
pip install bilibili-captions
```

## 使用

### CLI 命令行

```bash
# 下载字幕（优先 API，无字幕时 ASR）
bilibili-captions <BV号或URL> [模型大小]

# 示例
bilibili-captions BV16HqFBZE6N
bilibili-captions https://www.bilibili.com/video/BV16HqFBZE6N medium
```

### MCP 服务器

**发布后使用 uvx:**

```json
{
  "mcpServers": {
    "bilibili-captions": {
      "command": "uvx",
      "args": ["bilibili-captions"],
      "env": {
        "BILIBILI_SESSDATA": "你的 SESSDATA"
      },
      "timeout": 600000
    }
  }
}
```

**本地开发:**

```json
{
  "mcpServers": {
    "bilibili-captions": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/bilibili_captions",
        "bilibili-captions-mcp"
      ],
      "env": {
        "BILIBILI_SESSDATA": "你的 SESSDATA"
      },
      "timeout": 600000
    }
  }
}
```

## MCP 工具

### download_captions

下载 B 站视频字幕，支持多种格式。

**参数：**
- `url` (必需): B站视频URL或BV号
- `format` (可选): 输出格式，默认 `text`
  - `text` - 纯文本
  - `srt` - SRT字幕格式
  - `json` - JSON结构化
- `model_size` (可选): ASR模型大小，默认 `medium`
  - `base` / `small` / `medium` / `large`

**返回：**
```json
{
  "source": "bilibili_api" | "whisper_asr",
  "format": "text",
  "subtitle_count": 173,
  "content": "字幕内容...",
  "video_title": "视频标题"
}
```

## SESSDATA 获取

1. 登录 [B站](https://www.bilibili.com/)
2. F12 → Application → Cookies → `SESSDATA`
3. 复制值到环境变量或 `.env` 文件

## 依赖

- `yt-dlp` - 视频下载
- `ffmpeg` - 音频提取
- `faster-whisper` - 语音识别（或 `openai-whisper`）
- `opencc-python-reimplemented` - 繁简转换

## 许可证

MIT
