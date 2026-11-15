import os
import uuid
import yt_dlp

def download_youtube_video(url: str, output_dir: str) -> dict:
    """
    Downloads a video from YouTube using yt-dlp with max 1080p MP4 format.
    """
    os.makedirs(output_dir, exist_ok=True)
    unique_prefix = uuid.uuid4().hex[:8]
    out_template = os.path.join(output_dir, f"{unique_prefix}_%(title).50s.%(ext)s")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
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

        return {
            "video_id": os.path.basename(final_filename),
            "title": info.get("title", "YouTube Video"),
            "duration": info.get("duration", 0),
            "filepath": final_filename
        }
