import os
import subprocess
from .reframer import VideoReframer

QUALITY_PROFILES = {
    "720p": {
        "width": 720,
        "height": 1280,
        "crf": "23",
        "preset": "ultrafast",
        "audio_bitrate": "128k"
    },
    "1080p": {
        "width": 1080,
        "height": 1920,
        "crf": "20",
        "preset": "veryfast",
        "audio_bitrate": "192k"
    },
    "1440p": {
        "width": 1440,
        "height": 2560,
        "crf": "18",
        "preset": "veryfast",
        "audio_bitrate": "256k"
    }
}

class VideoRenderer:
    @staticmethod
    def check_audio_stream(video_path: str) -> bool:
        """Checks if input file contains an active audio stream."""
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_type",
            "-of", "csv=p=0",
            video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "audio" in res.stdout.decode()

    @classmethod
    def render_clip(
        cls,
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
        reframe_mode: str = "blurred_background",
        ass_path: str = None,
        video_quality: str = "1080p"
    ) -> str:
        """
        Extracts, reframes (to 9:16 vertical), sharpens foreground, smooths audio transitions,
        and renders video at requested quality (720p, 1080p, or 1440p).
        """
        duration = max(0.5, end_time - start_time)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        has_audio = cls.check_audio_stream(video_path)

        profile = QUALITY_PROFILES.get(video_quality, QUALITY_PROFILES["1080p"])
        w = profile["width"]
        h = profile["height"]
        crf = profile["crf"]
        preset = profile["preset"]
        audio_br = profile["audio_bitrate"]

        filters = []
        if reframe_mode == "center_crop":
            filters.append(
                f"[0:v]crop=ih*(9/16):ih:(iw-ow)/2:0,"
                f"scale={w}:{h}:flags=bicubic,"
                f"unsharp=5:5:0.6:5:5:0.0[v_base]"
            )
        else:
            # Cinematic Blurred Background:
            # - Background is scaled, cropped, heavily blurred, darkened (-18%), and given punchy contrast
            # - Foreground is scaled and sharpened with unsharp filter for crisp viewing on mobile
            filters.append(
                f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h},boxblur=30:5,eq=brightness=-0.18:contrast=1.15[bg];"
                f"[0:v]scale={w}:-2,unsharp=5:5:0.6:5:5:0.0[fg];"
                f"[bg][fg]overlay=0:({h}-overlay_h)/2[v_base]"
            )

        last_v_stream = "[v_base]"
        if ass_path and os.path.exists(ass_path):
            escaped_ass = ass_path.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
            filters.append(f"{last_v_stream}ass='{escaped_ass}'[v_out]")
            last_v_stream = "[v_out]"
        else:
            filters.append(f"{last_v_stream}null[v_out]")
            last_v_stream = "[v_out]"

        # Audio transition smoothing (fade-in & fade-out to prevent clicks and harsh cutoffs)
        fade_dur = min(0.2, duration / 4.0)
        out_start = max(0.0, duration - fade_dur)
        if has_audio:
            filters.append(f"[0:a]afade=t=in:ss=0:d={fade_dur:.2f},afade=t=out:st={out_start:.2f}:d={fade_dur:.2f}[a_out]")
            last_a_stream = "[a_out]"
        else:
            last_a_stream = None

        filter_str = ";".join(filters)

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-t", str(duration),
            "-i", video_path,
            "-filter_complex", filter_str,
            "-map", last_v_stream,
        ]

        if last_a_stream:
            cmd.extend(["-map", last_a_stream, "-c:a", "aac", "-b:a", audio_br])

        cmd.extend([
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", crf,
            "-pix_fmt", "yuv420p",
            output_path
        ])

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg render error: {res.stderr.decode('utf-8', errors='ignore')}")

        return output_path
