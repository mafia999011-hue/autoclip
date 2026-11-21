import os
import re
import uuid
import shutil
import subprocess
import yt_dlp

class LiveStreamRecorder:
    @staticmethod
    def inspect_url(url: str) -> dict:
        """Checks if a URL is currently live and returns channel/stream info."""
        node_path = shutil.which('node')
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web', 'mweb']
                }
            }
        }
        if node_path:
            ydl_opts['js_runtimes'] = {'node': {'path': node_path}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                is_live = bool(info.get('is_live') or info.get('live_status') in ['is_live', 'is_upcoming'])
                title = info.get('title') or "Live Stream"
                uploader = info.get('uploader') or info.get('channel') or "Streamer"
                thumbnail = info.get('thumbnail') or ""
                viewers = info.get('concurrent_view_count') or info.get('view_count') or 0
                category = (info.get('categories') or ["Live Streaming"])[0] if info.get('categories') else "Gaming / Entertainment"
                return {
                    "is_live": is_live,
                    "title": re.sub(r'[\r\n\t]+', ' ', title).strip(),
                    "uploader": uploader,
                    "thumbnail": thumbnail,
                    "viewers": viewers,
                    "category": category,
                    "url": url
                }
            except Exception as e:
                return {
                    "is_live": False,
                    "error": str(e),
                    "url": url
                }

    @staticmethod
    def record_live_snippet(url: str, output_dir: str, duration_seconds: int = 180, progress_callback = None) -> dict:
        """
        Connects to an ongoing live stream and captures a snippet of specified duration (in seconds).
        Uses stream copy for fast, zero-loss capture.
        """
        os.makedirs(output_dir, exist_ok=True)
        if progress_callback:
            progress_callback(f"Connecting to live broadcast: {url}...", 10)

        node_path = shutil.which('node')
        ydl_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
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
            info = ydl.extract_info(url, download=False)
            stream_url = info.get('url')
            if not stream_url and info.get('formats'):
                for f in reversed(info['formats']):
                    if f.get('url'):
                        stream_url = f['url']
                        break
            title = info.get('title') or "Live Stream"
            uploader = info.get('uploader') or info.get('channel') or "Streamer"

        if not stream_url:
            raise RuntimeError("Unable to resolve live stream URL. The streamer might be offline.")

        unique_id = uuid.uuid4().hex[:8]
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title)[:30].strip('_')
        output_filename = f"live_{unique_id}_{safe_title}.mp4"
        output_filepath = os.path.join(output_dir, output_filename)

        if progress_callback:
            progress_callback(f"🔴 Recording live snippet ({duration_seconds}s) from {uploader}...", 30)

        cmd = [
            "ffmpeg", "-y",
            "-i", stream_url,
            "-t", str(duration_seconds),
            "-c:v", "copy",
            "-c:a", "aac",
            output_filepath
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0 and not os.path.exists(output_filepath):
            raise RuntimeError(f"FFmpeg live recording failed: {res.stderr.decode('utf-8', errors='ignore')}")

        if progress_callback:
            progress_callback("Live snippet recorded successfully!", 100)

        return {
            "video_id": output_filename,
            "title": f"🔴 Live: {title}",
            "duration": duration_seconds,
            "platform": "Live Stream",
            "filepath": output_filepath
        }
