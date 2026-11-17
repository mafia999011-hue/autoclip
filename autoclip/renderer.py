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

PROGRESS_BAR_COLORS = {
    "hormozi": "0x00E6FF",      # Vibrant Yellow
    "mrbeast": "0x00FF66",      # Neon Green
    "cyberpunk": "0xFFFF00",    # Cyan
    "sunset": "0xFF00C8",       # Magenta / Pink
    "devin": "0x00A2FF",        # Gold / Red
    "minimal_clean": "0xFFA600" # Electric Blue
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
        video_quality: str = "1080p",
        enable_dynamic_zoom: bool = True,
        enable_progress_bar: bool = True,
        enable_color_pop: bool = True,
        enable_audio_boost: bool = True,
        subtitle_preset: str = "hormozi"
    ) -> str:
        """
        Extracts, reframes (to 9:16 vertical), sharpens foreground, smooths audio transitions,
        and renders video at requested quality (720p, 1080p, or 1440p) with viral editing features.
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

        color_filter = ",eq=saturation=1.16:contrast=1.08:brightness=-0.02" if enable_color_pop else ""

        filters = []
        if reframe_mode == "center_crop":
            # Dynamic punch-in zoom for center crop (crops center 9:16 region with PTS-preserving 1.08x punch-in)
            if enable_dynamic_zoom:
                crop_expr = "crop='w=if(lt(mod(t,6),3.4), ih*(9/16), ih*(9/16)*0.92)':h='if(lt(mod(t,6),3.4), ih, ih*0.92)':x=(iw-ow)/2:y=(ih-oh)/2"
            else:
                crop_expr = "crop=ih*(9/16):ih:(iw-ow)/2:0"
            filters.append(
                f"[0:v]{crop_expr},"
                f"scale={w}:{h}:flags=bicubic,"
                f"unsharp=5:5:0.6:5:5:0.0{color_filter}[v_base]"
            )
        else:
            # Cinematic Blurred Background:
            # - Background is scaled, cropped, heavily blurred, darkened (-18%), and given punchy contrast
            # - Foreground has dynamic punch-in zoom using framerate-preserving crop, scaled, sharpened & color boosted
            if enable_dynamic_zoom:
                fg_crop = "crop='w=if(lt(mod(t,6),3.4), iw, iw*0.92)':h='if(lt(mod(t,6),3.4), ih, ih*0.92)':x=(iw-ow)/2:y=(ih-oh)/2,"
            else:
                fg_crop = ""
            filters.append(
                f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h},boxblur=30:5,eq=brightness=-0.18:contrast=1.15[bg];"
                f"[0:v]{fg_crop}scale={w}:-2,unsharp=5:5:0.6:5:5:0.0{color_filter}[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2[v_base]"
            )

        last_v_stream = "[v_base]"

        # Animated bottom retention progress bar (draws underneath subtitles)
        if enable_progress_bar:
            bar_color = PROGRESS_BAR_COLORS.get(subtitle_preset, "0x00E6FF")
            bar_h = max(8, int(12 * (h / 1920)))
            filters.append(
                f"{last_v_stream}drawbox=x=0:y={h}-{bar_h}:w={w}:h={bar_h}:color=black@0.45:t=fill,"
                f"drawbox=x=0:y={h}-{bar_h}:w='min({w},{w}*t/{duration:.2f})':h={bar_h}:color={bar_color}:t=fill[v_prog]"
            )
            last_v_stream = "[v_prog]"

        if ass_path and os.path.exists(ass_path):
            escaped_ass = ass_path.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
            filters.append(f"{last_v_stream}ass='{escaped_ass}'[v_out]")
            last_v_stream = "[v_out]"
        else:
            filters.append(f"{last_v_stream}null[v_out]")
            last_v_stream = "[v_out]"

        # Audio transition smoothing + optional vocal presence boost for phone speakers
        fade_dur = min(0.2, duration / 4.0)
        out_start = max(0.0, duration - fade_dur)
        if has_audio:
            if enable_audio_boost:
                filters.append(
                    f"[0:a]afade=t=in:ss=0:d={fade_dur:.2f},afade=t=out:st={out_start:.2f}:d={fade_dur:.2f},"
                    f"acompressor=threshold=-18dB:ratio=3:attack=5:release=50,volume=1.2[a_out]"
                )
            else:
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
            "-avoid_negative_ts", "make_zero",
            output_path
        ])

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg render error: {res.stderr.decode('utf-8', errors='ignore')}")

        return output_path
