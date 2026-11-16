import os
import re

EMOJI_KEYWORDS = {
    # English Keywords
    "MONEY": "💰", "CASH": "💵", "RICH": "🤑", "PROFIT": "📈", "DOLLAR": "💵", "BILLION": "💎", "MILLION": "💎",
    "FIRE": "🔥", "LIT": "🔥", "HOT": "🔥", "BURN": "🔥",
    "ROCKET": "🚀", "GROWTH": "🚀", "SUCCESS": "🏆", "WIN": "🏆", "WINNER": "🏆", "BEST": "🥇", "TOP": "🔝",
    "SECRET": "🤫", "HACK": "⚡", "TRICK": "🎯", "CHALLENGE": "🎯", "GOAL": "🎯",
    "MIND": "🧠", "BRAIN": "🧠", "THINK": "💡", "IDEA": "💡",
    "CRAZY": "🤯", "INSANE": "🤯", "SHOCKING": "😱", "WOW": "😲", "UNBELIEVABLE": "🤯",
    "TIME": "⏳", "CLOCK": "⏰", "WAIT": "⏱️", "NOW": "⚡", "FAST": "⚡", "SPEED": "🏎️",
    "LOVE": "❤️", "HEART": "❤️", "PASSION": "❤️", "CARE": "❤️",
    "WARNING": "⚠️", "DANGER": "🚨", "MISTAKE": "❌", "STOP": "🛑", "WRONG": "❌", "ALERT": "🚨",
    "QUESTION": "❓", "WHY": "❓", "HOW": "❓", "WHAT": "❓",
    "STRONG": "💪", "POWER": "⚡", "ENERGY": "⚡", "BEAST": "🦁",
    "KILLER": "💀", "DEAD": "💀", "GAME": "🎮", "GAMING": "🎮", "CONTROLLER": "🎮",
    "PHONE": "📱", "MOBILE": "📱", "COMPUTER": "💻", "PC": "💻", "CAMERA": "📸", "MIC": "🎙️",
    "FREE": "🎁", "GIFT": "🎁", "LUCK": "🍀", "CAR": "🚗",

    # Hinglish & Hindi Keywords
    "PAISA": "💰", "PAISE": "💰", "AMEER": "🤑", "DAULAT": "💵", "LAKH": "💰", "CRORE": "💰",
    "AAG": "🔥", "DHAMAKA": "💥", "BOMB": "💣", "KHATARNAK": "⚡",
    "JEET": "🏆", "JEETA": "🏆", "KAMIYAB": "🚀", "NUMBER1": "🥇", "BAAP": "👑", "KING": "👑", "RAJA": "👑",
    "RAAZ": "🤫", "SECRET": "🤫", "CHHUPA": "🤫", "CHORI": "🕵️",
    "DIMAG": "🧠", "SOCH": "💡", "IDEA": "💡", "SAMJH": "💡",
    "PAGAL": "🤯", "GAJAB": "🤯", "BAWAL": "💥", "SHANDAR": "✨", "JADU": "🪄",
    "WAQT": "⏳", "SAMAY": "⏰", "ROKO": "🛑", "JALDI": "⚡", "TURANT": "⚡",
    "DIL": "❤️", "PYAR": "❤️", "JAAN": "❤️", "DOST": "🤝", "YAAR": "🤝",
    "GALTI": "❌", "KHATRA": "⚠️", "KHARAB": "❌", "MAT": "🛑", "DHOKA": "⚠️", "JHUTH": "🤥",
    "SACH": "💯", "ASLI": "💎", "NAQLI": "🤡",
    "KYU": "❓", "KYA": "❓", "KAISE": "❓", "KAB": "❓", "KAUN": "❓",
    "TAQAT": "💪", "DUM": "💪", "MAZA": "🥳", "HASI": "😂", "ROYA": "😭"
}

STYLE_PRESETS = {
    "hormozi": {
        "name": "Hormozi Yellow",
        "highlight": "&H0000FFFF&", # Yellow (\c&H0000FFFF&)
        "base": "&H00FFFFFF&",      # White (\c&H00FFFFFF&)
        "outline": "&H00000000&",   # Black
        "font_size": 76,
        "outline_w": 8
    },
    "mrbeast": {
        "name": "MrBeast Neon Green",
        "highlight": "&H0000FF00&", # Neon Green
        "base": "&H00FFFFFF&",
        "outline": "&H00000000&",
        "font_size": 76,
        "outline_w": 8
    },
    "cyberpunk": {
        "name": "Cyberpunk Cyan",
        "highlight": "&H00FFFF00&", # Cyan
        "base": "&H00FFFFFF&",
        "outline": "&H004A0080&",   # Dark purple
        "font_size": 74,
        "outline_w": 8
    },
    "sunset": {
        "name": "Sunset Pink",
        "highlight": "&H00FF00FF&", # Magenta
        "base": "&H00FFFFFF&",
        "outline": "&H00000000&",
        "font_size": 74,
        "outline_w": 8
    }
}

class SubtitleGenerator:
    @staticmethod
    def format_ass_time(seconds: float) -> str:
        seconds = max(0.0, seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"

    @classmethod
    def generate_ass(
        cls,
        words: list,
        clip_start: float,
        clip_end: float,
        output_ass_path: str,
        preset_name: str = "hormozi",
        enable_emojis: bool = True,
        words_per_group: int = 2,
        video_quality: str = "1080p"
    ) -> str:
        preset = STYLE_PRESETS.get(preset_name, STYLE_PRESETS["hormozi"])
        highlight_color = preset["highlight"]
        base_color = preset["base"]
        outline_color = preset["outline"]

        if video_quality == "720p":
            res_x, res_y = 720, 1280
            font_size = int(preset["font_size"] * (720 / 1080))
            outline_w = max(4, int(preset["outline_w"] * (720 / 1080)))
            margin_v = int(480 * (1280 / 1920))
        elif video_quality == "1440p":
            res_x, res_y = 1440, 2560
            font_size = int(preset["font_size"] * (1440 / 1080))
            outline_w = int(preset["outline_w"] * (1440 / 1080))
            margin_v = int(480 * (2560 / 1920))
        else:  # 1080p
            res_x, res_y = 1080, 1920
            font_size = preset["font_size"]
            outline_w = preset["outline_w"]
            margin_v = 480

        valid_words = []
        for w in words:
            try:
                raw_s = float(w.get("start", 0.0))
                raw_e = float(w.get("end", raw_s + 0.3))
            except (ValueError, TypeError):
                continue

            w_start = raw_s - clip_start
            w_end = raw_e - clip_start
            raw_word = str(w.get("word", "")).strip().upper()
            if not raw_word:
                continue

            clean_word = re.sub(r'[^A-Z0-9]', '', raw_word)
            emoji_tag = ""
            if enable_emojis and clean_word in EMOJI_KEYWORDS:
                emoji_tag = f" {EMOJI_KEYWORDS[clean_word]}"

            if w_end >= 0 and w_start <= (clip_end - clip_start):
                valid_words.append({
                    "word": raw_word + emoji_tag,
                    "start": max(0.0, w_start),
                    "end": max(0.05, w_end)
                })

        # Group words into punchy 2-word chunks (Opus Clip / Hormozi pacing)
        chunks = []
        for i in range(0, len(valid_words), words_per_group):
            chunks.append(valid_words[i:i + words_per_group])

        # Modern high-impact vertical subtitle styling matching target resolution
        ass_content = [
            "[Script Info]",
            "ScriptType: v4.00+",
            f"PlayResX: {res_x}",
            f"PlayResY: {res_y}",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Default,Arial,{font_size},{base_color},&H000000FF&,{outline_color},&H80000000&,-1,0,0,0,100,100,2,0,1,{outline_w},4,2,60,60,{margin_v},1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        for chunk in chunks:
            for active_idx, target_word in enumerate(chunk):
                w_start = target_word["start"]
                w_end = target_word["end"]
                if w_end <= w_start:
                    w_end = w_start + 0.3

                line_parts = []
                for idx, item in enumerate(chunk):
                    if idx == active_idx:
                        # Animated active pop / bounce effect with highlight color
                        line_parts.append(
                            r"{\fscx115\fscy115\c" + highlight_color + r"\b1}" +
                            item["word"] +
                            r"{\fscx100\fscy100\c" + base_color + r"\b1}"
                        )
                    else:
                        line_parts.append(item["word"])

                text_str = " ".join(line_parts)
                start_str = cls.format_ass_time(w_start)
                end_str = cls.format_ass_time(w_end)

                ass_content.append(
                    f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text_str}"
                )

        os.makedirs(os.path.dirname(os.path.abspath(output_ass_path)), exist_ok=True)
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ass_content))

        return output_ass_path
