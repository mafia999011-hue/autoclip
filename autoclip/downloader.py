import os
import re
import uuid
import yt_dlp

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

def download_online_video(url: str, output_dir: str) -> dict:
    """
    Downloads video from YouTube, Twitch (Clips / VODs), and other supported sites using yt-dlp.
    """
    os.makedirs(output_dir, exist_ok=True)
    platform = detect_platform(url)
    unique_prefix = uuid.uuid4().hex[:8]
    out_template = os.path.join(output_dir, f"{unique_prefix}_%(title).50s.%(ext)s")
    
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    
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
