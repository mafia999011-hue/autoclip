import subprocess
import json

class VideoReframer:
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """Fetch video duration, width, height using ffprobe."""
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration:format=duration",
            "-of", "json",
            video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            return {"width": 1920, "height": 1080, "duration": 60.0}
        
        try:
            data = json.loads(res.stdout.decode())
            streams = data.get("streams", [{}])[0]
            fmt = data.get("format", {})
            width = int(streams.get("width", 1920))
            height = int(streams.get("height", 1080))
            dur_str = streams.get("duration") or fmt.get("duration") or "60.0"
            duration = float(dur_str)
            return {"width": width, "height": height, "duration": duration}
        except Exception:
            return {"width": 1920, "height": 1080, "duration": 60.0}

    @staticmethod
    def get_filter_complex(mode: str = "blurred_background", width: int = 1080, height: int = 1920) -> str:
        """
        Returns the FFmpeg filter_complex string for vertical 9:16.
        """
        if mode == "center_crop":
            # Crop center 9:16 region
            return f"[0:v]crop=ih*(9/16):ih:(iw-ow)/2:0,scale={width}:{height}:flags=bicubic[v_reframed]"
        
        # Default: Blurred background with centered 16:9 subject
        return (
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},boxblur=25:5[bg];"
            f"[0:v]scale={width}:-2[fg];"
            f"[bg][fg]overlay=0:({height}-overlay_h)/2[v_reframed]"
        )
