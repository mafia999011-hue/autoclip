import os
import subprocess
from .reframer import VideoReframer

class VideoRenderer:
    @staticmethod
    def render_clip(
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
        reframe_mode: str = "blurred_background",
        ass_path: str = None
    ) -> str:
        """
        Extracts, reframes (to 9:16), and burns subtitles onto a short clip.
        """
        duration = max(0.5, end_time - start_time)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Build filter_complex
        filters = []
        if reframe_mode == "center_crop":
            filters.append("[0:v]crop=ih*(9/16):ih:(iw-ow)/2:0,scale=1080:1920:flags=bicubic[v_base]")
        else:
            # Blurred background mode
            filters.append(
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,boxblur=25:5[bg];"
                "[0:v]scale=1080:-2[fg];"
                "[bg][fg]overlay=0:(1920-overlay_h)/2[v_base]"
            )

        last_stream = "[v_base]"
        if ass_path and os.path.exists(ass_path):
            # Escape path for FFmpeg filter syntax
            escaped_ass = ass_path.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
            filters.append(f"{last_stream}ass='{escaped_ass}'[v_out]")
            last_stream = "[v_out]"
        else:
            filters.append(f"{last_stream}null[v_out]")
            last_stream = "[v_out]"

        filter_str = ";".join(filters)

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-t", str(duration),
            "-i", video_path,
            "-filter_complex", filter_str,
            "-map", last_stream,
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "ultrafast",  # Fast rendering on mobile/ARM64
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg render error: {res.stderr.decode('utf-8', errors='ignore')}")

        return output_path
