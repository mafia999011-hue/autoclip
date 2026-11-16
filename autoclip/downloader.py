import os
import re
import uuid
import shutil
import yt_dlp
from .live_recorder import LiveStreamRecorder

def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "twitch.tv" in url_lower:
        return "Twitch"
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "YouTube"
    if "tiktok.com" in url_lower:
        return "TikTok"
    if "twitter.com" in url_lower or "x.com" in url_lower:
        return "X / Twitter"
    if "kick.com" in url_lower:
        return "Kick"
    return "Web Video"

def download_online_video(url: str, output_dir: str, live_duration: int = 180) -> dict:
    """
    Downloads video from YouTube, Twitch, etc.
    If the link is an ongoing live stream, automatically captures a live snippet!
    Bypasses YouTube bot verification using mobile android player client.
    """
    os.makedirs(output_dir, exist_ok=True)
    platform = detect_platform(url)

    # 1. First probe if this URL is an active live stream
    live_info = LiveStreamRecorder.inspect_url(url)
    if live_info.get("is_live"):
        return LiveStreamRecorder.record_live_snippet(
            url=url,
            output_dir=output_dir,
            duration_seconds=live_duration
        )

    # 2. Standard video or clip download
    unique_prefix = uuid.uuid4().hex[:8]
    out_template = os.path.join(output_dir, f"{unique_prefix}_%(title).50s.%(ext)s")
    
    node_path = shutil.which('node')
    ydl_opts = {
        'format': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]/bestvideo+bestaudio/best',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'mweb']
            }
        }
    }
    if node_path:
        ydl_opts['js_runtimes'] = {'node': {'path': node_path}}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        final_filename = f"{base}.mp4"
        if not os.path.exists(final_filename) and os.path.exists(filename):
            final_filename = filename

        raw_title = info.get("title") or f"{platform} Video"
        clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title).strip()

        return {
            "video_id": os.path.basename(final_filename),
            "title": clean_title,
            "duration": info.get("duration", 0),
            "platform": platform,
            "filepath": final_filename
        }

# Backwards compatibility alias
download_youtube_video = download_online_video
