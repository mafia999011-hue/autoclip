import os
import re
from .reframer import VideoReframer
from .gemini_client import GeminiClipperClient
from .subtitler import SubtitleGenerator
from .renderer import VideoRenderer
from .storage import HistoryStorage

class AutoClipPipeline:
    def __init__(self, api_key: str = None, output_dir: str = "output"):
        self.api_key = api_key
        self.output_dir = output_dir
        self.client = GeminiClipperClient(api_key=api_key)

    def process_video(
        self,
        video_path: str,
        reframe_mode: str = "blurred_background",
        subtitle_preset: str = "hormozi",
        enable_emojis: bool = True,
        length_pref: str = "auto",
        clip_count: str = "3",
        progress_callback = None
    ) -> dict:
        def update_progress(stage: str, percent: int):
            if progress_callback:
                progress_callback(stage, percent)

        update_progress("Inspecting video metadata", 10)
        info = VideoReframer.get_video_info(video_path)
        video_duration = info.get("duration", 60.0)

        update_progress("Extracting audio track for Opus AI engine", 25)
        audio_path = self.client.extract_audio(video_path)

        update_progress(f"Analyzing virality & hooks (Target: {clip_count} clips)", 45)
        ai_result = self.client.analyze_video_audio(audio_path, video_duration, length_pref=length_pref, clip_count=clip_count)

        clips_data = ai_result.get("clips", [])
        rendered_clips = []
        total_clips = len(clips_data)

        for idx, clip in enumerate(clips_data):
            c_id = clip.get("id", idx + 1)
            title = clip.get("title", f"Clip {c_id}")
            start_t = float(clip.get("start_time", 0.0))
            end_t = float(clip.get("end_time", min(video_duration, start_t + 30.0)))
            words = clip.get("words", [])

            slug = re.sub(r'[^a-zA-Z0-9_-]', '_', title)[:25].strip('_')
            clip_base = f"clip_{c_id}_{slug}"

            ass_path = os.path.join(self.output_dir, f"{clip_base}.ass")
            clip_output_path = os.path.join(self.output_dir, f"{clip_base}.mp4")

            # Generate ASS subtitles with Opus auto-emojis and preset style
            SubtitleGenerator.generate_ass(
                words=words,
                clip_start=start_t,
                clip_end=end_t,
                output_ass_path=ass_path,
                preset_name=subtitle_preset,
                enable_emojis=enable_emojis
            )

            progress_pct = 50 + int((idx + 1) / total_clips * 45)
            update_progress(f"Rendering Clip {c_id}/{total_clips}: {title}", progress_pct)

            VideoRenderer.render_clip(
                video_path=video_path,
                start_time=start_t,
                end_time=end_t,
                output_path=clip_output_path,
                reframe_mode=reframe_mode,
                ass_path=ass_path
            )

            rendered_clips.append({
                "id": c_id,
                "title": title,
                "hook": clip.get("hook", ""),
                "start_time": start_t,
                "end_time": end_t,
                "duration": round(end_t - start_t, 1),
                "virality_score": clip.get("virality_score", 90),
                "hook_score": clip.get("hook_score", 88),
                "flow_score": clip.get("flow_score", 92),
                "engagement_score": clip.get("engagement_score", 94),
                "reason": clip.get("reason", ""),
                "social_copy": clip.get("social_copy", {}),
                "video_file": os.path.basename(clip_output_path),
                "download_url": f"/download/{os.path.basename(clip_output_path)}",
                "preview_url": f"/stream/{os.path.basename(clip_output_path)}"
            })

        # Save to persistent history
        try:
            HistoryStorage(os.path.join(os.path.dirname(self.output_dir), "data", "history.json")).save_clips(rendered_clips)
        except Exception as e:
            print(f"Warning: Failed to save to history: {e}")

        update_progress("Complete! All Opus-style clips rendered successfully.", 100)

        return {
            "summary": ai_result.get("full_summary", ""),
            "original_duration": video_duration,
            "clips": rendered_clips
        }
