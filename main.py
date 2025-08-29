# /// script
# dependencies = ["requests", "openai-whisper"]
# ///

import sys
import requests
import json
import subprocess
import os
import re

# 尝试导入 whisper，如果失败则提示用户安装
try:
    import whisper
except ImportError:
    print("错误: whisper 库未安装。")
    print("请使用 'pip install openai-whisper' 命令进行安装。")
    sys.exit(1)

def make_safe_filename(filename):
    """移除或替换文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_video_info(url):
    """获取B站视频的标题和CID"""
    try:
        # 伪装成浏览器发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        # 从URL中提取BV号
        bvid = url.split('/')[-2] if 'video' in url else url.split('/')[-1]

        # 获取视频信息的API
        info_api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"

        response = requests.get(info_api_url, headers=headers)
        response.raise_for_status() # 如果请求失败则抛出异常

        data = response.json()
        if data['code'] == 0:
            video_title = data['data']['title']
            cid = data['data']['cid']
            return video_title, cid, bvid
        else:
            print(f"错误: 无法获取视频信息。B站返回: {data['message']}")
            return None, None
    except Exception as e:
        print(f"错误: 获取视频信息时出错: {e}")
        return None, None

def get_subtitles_from_bilibili(video_title, cid, bvid):
    """尝试从B站下载已有的字幕"""
    try:
        subtitle_api_url = f"https://api.bilibili.com/x/player/v2?cid={cid}&bvid={bvid}" # 需要bvid
        response = requests.get(subtitle_api_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        data = response.json()

        if data['code'] == 0 and data['data']['subtitle']['list']:
            subtitle_list = data['data']['subtitle']['list']
            print(f"发现 {len(subtitle_list)} 个可用字幕。")

            # 通常选择第一个字幕
            subtitle_url = subtitle_list[0]['subtitle_url']
            if not subtitle_url.startswith('http'):
                subtitle_url = 'https:' + subtitle_url

            subtitle_data_json = requests.get(subtitle_url).json()

            # 将B站JSON格式的字幕转换为SRT格式
            srt_content = ""
            for i, item in enumerate(subtitle_data_json['body']):
                start_time = item['from']
                end_time = item['to']
                content = item['content']

                # 转换时间格式
                start_h, start_m, start_s = int(start_time // 3600), int((start_time % 3600) // 60), start_time % 60
                end_h, end_m, end_s = int(end_time // 3600), int((end_time % 3600) // 60), end_time % 60

                srt_content += f"{i+1}\n"
                srt_content += f"{start_h:02}:{start_m:02}:{f'{start_s:.3f}'.replace('.', ',')}"
                srt_content += f" --> {end_h:02}:{f'{end_m:02}'}:{f'{end_s:.3f}'.replace('.', ',')}\n"
                srt_content += f"{content}\n\n"

            safe_title = make_safe_filename(video_title)
            subtitle_filename = f"{safe_title}.srt"
            with open(subtitle_filename, 'w', encoding='utf-8') as f:
                f.write(srt_content)

            print(f"字幕下载成功！已保存为: {subtitle_filename}")
            return True
        else:
            print("该视频没有自带字幕。")
            return False

    except Exception as e:
        print(f"错误: 检查或下载字幕时发生未知错误: {e}")
        return False

def generate_subtitles_with_asr(video_url, safe_video_title):
    """使用ASR技术生成字幕"""
    print("\n--- 步骤 2: 正在下载视频并提取音频用于ASR ---")
    try:
        video_filename = f"{safe_video_title}.mp4"
        audio_filename = f"{safe_video_title}.wav"

        # 使用 yt-dlp 下载视频
        print(f"正在下载视频: {video_url}")
        subprocess.run(['yt-dlp', '-o', video_filename, video_url], check=True)
        print("视频下载完成。")

        # 使用 ffmpeg 提取音频
        print("正在提取音频...")
        subprocess.run(['ffmpeg', '-i', video_filename, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_filename], check=True)
        print("音频提取完成。")

        # 使用Whisper生成字幕
        print("正在使用Whisper生成字幕...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_filename)

        # 保存为SRT格式
        srt_filename = f"{safe_video_title}_asr.srt"
        with open(srt_filename, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments']):
                start = segment['start']
                end = segment['end']
                text = segment['text'].strip()

                # 转换时间格式为SRT要求的格式
                start_time = f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}".replace('.', ',')
                end_time = f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}".replace('.', ',')

                f.write(f"{i+1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

        print(f"ASR字幕生成成功！已保存为: {srt_filename}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"错误: 外部命令执行失败: {e}")
        return False
    except Exception as e:
        print(f"错误: 生成字幕时发生未知错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python main.py <B站视频URL>")
        sys.exit(1)

    video_url = sys.argv[1]
    video_title, cid, bvid = get_video_info(video_url)
    
    if not all([video_title, cid, bvid]):
        print("无法获取视频信息，程序退出。")
        sys.exit(1)

    safe_title = make_safe_filename(video_title)
    
    # 尝试下载现有字幕
    if not get_subtitles_from_bilibili(video_title, cid, bvid):
        # 如果没有现有字幕，则使用ASR生成
        generate_subtitles_with_asr(video_url, safe_title)