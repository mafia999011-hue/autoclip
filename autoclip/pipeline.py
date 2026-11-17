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
        caption_language: str = "auto",
        video_quality: str = "1080p",
        show_hook_header: bool = True,
        enable_dynamic_zoom: bool = True,
        enable_progress_bar: bool = True,
        enable_color_pop: bool = True,
        enable_audio_boost: bool = True,
        progress_callback = None
    ) -> dict:
        def update_progress(stage: str, percent: int):
            if progress_callback:
                progress_callback(stage, percent)

        update_progress("Inspecting video metadata", 10)
        info = VideoReframer.get_video_info(video_path)
        video_duration = info.get("duration", 60.0)

        update_progress("Extracting audio track for Opus AI engine", 25)
        audio_path = self.client.extract_audio(video_path, video_duration=video_duration)

        update_progress(f"Analyzing virality & hooks ({caption_language.upper()} script, {clip_count} clips)", 45)
        ai_result = self.client.analyze_video_audio(
            audio_path,
            video_duration,
            length_pref=length_pref,
            clip_count=clip_count,
            caption_language=caption_language
        )

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

            # Subtle acoustic safety padding: 0.15s pre-roll and 0.25s post-roll
            # to preserve starting/ending consonants and prevent jarring cuts
            safe_start = max(0.0, start_t - 0.15)
            safe_end = min(video_duration, end_t + 0.25)
            clip_dur = max(0.5, safe_end - safe_start)

            # Phase 2 (Micro): Transcribe exact speech for this specific clip to achieve 100% voice-accurate subtitles
            progress_pct = 50 + int((idx + 1) / total_clips * 45)
            update_progress(f"Transcribing voice timestamps for Clip {c_id}/{total_clips}...", max(10, progress_pct - 5))
            precise_words = self.client.transcribe_clip_audio(
                audio_path=audio_path,
                start_time=safe_start,
                duration=clip_dur,
                caption_language=caption_language
            )

            # If micro-snippet speech transcription returned empty (offline or music video),
            # fall back gracefully to timed hook/title words so subtitles are never blank
            if not precise_words:
                fallback_text = clip.get("hook") or clip.get("title", "")
                tokens = [tok for tok in re.split(r'\s+', fallback_text) if tok.strip()]
                if tokens:
                    word_interval = min(0.45, max(0.2, clip_dur / max(1, len(tokens))))
                    precise_words = []
                    for i, tok in enumerate(tokens):
                        w_s = round(i * word_interval, 2)
                        w_e = round(min(clip_dur, (i + 1) * word_interval), 2)
                        precise_words.append({"word": tok, "start": w_s, "end": w_e})

            hook_headline = clip.get("hook_headline") or title

            # Generate ASS subtitles with Opus auto-emojis, active bounce, top hook banner, and punchy 2-word groups
            # precise_words are already relative to safe_start (starting from 0.0s)
            SubtitleGenerator.generate_ass(
                words=precise_words,
                clip_start=0.0,
                clip_end=clip_dur,
                output_ass_path=ass_path,
                preset_name=subtitle_preset,
                enable_emojis=enable_emojis,
                words_per_group=2,
                video_quality=video_quality,
                hook_headline=hook_headline,
                show_hook_header=show_hook_header
            )

            update_progress(f"Rendering Clip {c_id}/{total_clips}: {title} ({video_quality})", progress_pct)

            VideoRenderer.render_clip(
                video_path=video_path,
                start_time=safe_start,
                end_time=safe_end,
                output_path=clip_output_path,
                reframe_mode=reframe_mode,
                ass_path=ass_path,
                video_quality=video_quality,
                enable_dynamic_zoom=enable_dynamic_zoom,
                enable_progress_bar=enable_progress_bar,
                enable_color_pop=enable_color_pop,
                enable_audio_boost=enable_audio_boost,
                subtitle_preset=subtitle_preset
            )

            rendered_clips.append({
                "id": c_id,
                "title": title,
                "hook": clip.get("hook", ""),
                "hook_headline": hook_headline,
                "hook_type": clip.get("hook_type", "⚡ Value Bomb & Hack"),
                "curiosity_gap": clip.get("curiosity_gap", "9.6/10"),
                "drop_off_risk": clip.get("drop_off_risk", "Very Low"),
                "viral_action_tip": clip.get("viral_action_tip", "Pin an engaging question in comments to increase algorithmic watch time."),
                "start_time": safe_start,
                "end_time": safe_end,
                "duration": round(safe_end - safe_start, 1),
                "quality": video_quality,
                "virality_score": clip.get("virality_score", 95),
                "hook_score": clip.get("hook_score", 96),
                "flow_score": clip.get("flow_score", 94),
                "engagement_score": clip.get("engagement_score", 95),
                "reason": clip.get("reason", ""),
                "social_copy": clip.get("social_copy", {}),
                "video_file": os.path.basename(clip_output_path),
                "download_url": f"/download/{os.path.basename(clip_output_path)}",
                "preview_url": f"/stream/{os.path.basename(clip_output_path)}"
            })

        # Save to persistent history
        try:
            HistoryStorage(os.path.join(os.path.dirname(os.path.abspath(self.output_dir)), "data", "history.json")).save_clips(rendered_clips)
        except Exception as e:
            print(f"Warning: Failed to save to history: {e}")

        update_progress("Complete! All Money Clip shorts rendered successfully.", 100)

        return {
            "summary": ai_result.get("full_summary", ""),
            "original_duration": video_duration,
            "clips": rendered_clips
        }
