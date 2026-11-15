import os
import json
from datetime import datetime

class HistoryStorage:
    def __init__(self, data_file: str = "data/history.json"):
        self.data_file = data_file
        os.makedirs(os.path.dirname(os.path.abspath(self.data_file)), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_all_clips(self) -> list:
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                clips = json.load(f)
                return sorted(clips, key=lambda x: x.get("created_at", ""), reverse=True)
        except Exception:
            return []

    def save_clips(self, new_clips: list):
        current = self.get_all_clips()
        existing_files = {c.get("video_file") for c in current}
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        for clip in new_clips:
            v_file = clip.get("video_file")
            if v_file and v_file not in existing_files:
                clip_copy = dict(clip)
                clip_copy["created_at"] = now_str
                current.append(clip_copy)

        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)

    def delete_clip(self, video_file: str, output_dir: str = "output") -> bool:
        clips = self.get_all_clips()
        updated = [c for c in clips if c.get("video_file") != video_file]
        
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(updated, f, indent=2)

        # Remove video file and associated ASS file if they exist
        video_path = os.path.join(output_dir, video_file)
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception:
                pass

        base, _ = os.path.splitext(video_file)
        ass_path = os.path.join(output_dir, f"{base}.ass")
        if os.path.exists(ass_path):
            try:
                os.remove(ass_path)
            except Exception:
                pass

        return True
