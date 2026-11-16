import os
import re

EMOJI_KEYWORDS = {
    # English
    "MONEY": "💰", "CASH": "💵", "RICH": "🤑", "PROFIT": "📈", "DOLLAR": "💵",
    "FIRE": "🔥", "LIT": "🔥", "HOT": "🔥",
    "ROCKET": "🚀", "GROWTH": "🚀", "SUCCESS": "🏆", "WIN": "🏆", "WINNER": "🏆",
    "SECRET": "🤫", "HACK": "⚡", "TRICK": "🎯",
    "MIND": "🧠", "BRAIN": "🧠", "THINK": "💡", "IDEA": "💡",
    "CRAZY": "🤯", "INSANE": "🤯", "SHOCKING": "😱", "WOW": "😲",
    "TIME": "⏳", "CLOCK": "⏰", "WAIT": "⏱️",
    "LOVE": "❤️", "HEART": "❤️", "PASSION": "❤️",
    "WARNING": "⚠️", "DANGER": "🚨", "MISTAKE": "❌", "STOP": "🛑",
    "QUESTION": "❓", "WHY": "❓", "HOW": "❓",
    "STRONG": "💪", "POWER": "⚡", "ENERGY": "⚡",
    "KILLER": "💀", "DEAD": "💀", "GAME": "🎮", "CONTROLLER": "🎮",

    # Hinglish & Hindi Keywords
    "PAISA": "💰", "PAISE": "💰", "AMEER": "🤑", "DAULAT": "💵",
    "AAG": "🔥", "DHAMAKA": "💥", "BOMB": "💣",
    "JEET": "🏆", "JEETA": "🏆", "KAMIYAB": "🚀", "NUMBER1": "🥇",
    "BAAP": "👑", "KING": "👑", "RAJA": "👑",
    "RAAZ": "🤫", "SECRET": "🤫", "CHHUPA": "🤫",
    "DIMAG": "🧠", "SOCH": "💡", "IDEA": "💡", "SAMJH": "💡",
    "PAGAL": "🤯", "GAJAB": "🤯", "BAWAL": "💥", "SHANDAR": "✨",
    "WAQT": "⏳", "SAMAY": "⏰", "ROKO": "🛑",
    "DIL": "❤️", "PYAR": "❤️", "JAAN": "❤️",
    "GALTI": "❌", "KHATRA": "⚠️", "KHARAB": "❌", "MAT": "🛑", "DHOKA": "⚠️",
    "KYU": "❓", "KYA": "❓", "KAISE": "❓", "KAB": "❓",
    "TAQAT": "💪", "DUM": "💪", "MAZA": "🥳", "KHATARNAK": "⚡"
}

STYLE_PRESETS = {
    "hormozi": {
        "name": "Hormozi Yellow",
        "highlight": "&H0000FFFF&", # Yellow
        "base": "&H00FFFFFF&",      # White
        "outline": "&H00000000&",   # Black
        "font_size": 60,
        "outline_w": 7
    },
    "mrbeast": {
        "name": "MrBeast Neon Green",
        "highlight": "&H0000FF00&", # Neon Green
        "base": "&H00FFFFFF&",
        "outline": "&H00000000&",
        "font_size": 62,
        "outline_w": 8
    },
    "cyberpunk": {
        "name": "Cyberpunk Cyan",
        "highlight": "&H00FFFF00&", # Cyan
        "base": "&H00FFFFFF&",
        "outline": "&H004A0080&",   # Dark purple
        "font_size": 58,
        "outline_w": 6
    },
    "sunset": {
        "name": "Sunset Pink",
        "highlight": "&H00FF00FF&", # Magenta
        "base": "&H00FFFFFF&",
        "outline": "&H00000000&",
        "font_size": 58,
        "outline_w": 6
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
        words_per_group: int = 4
    ) -> str:
        preset = STYLE_PRESETS.get(preset_name, STYLE_PRESETS["hormozi"])
        highlight_color = preset["highlight"]
        base_color = preset["base"]
        outline_color = preset["outline"]
        font_size = preset["font_size"]
        outline_w = preset["outline_w"]

        valid_words = []
        for w in words:
            w_start = w.get("start", 0.0) - clip_start
            w_end = w.get("end", 0.0) - clip_start
            raw_word = w.get("word", "").strip().upper()
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

        chunks = []
        for i in range(0, len(valid_words), words_per_group):
            chunks.append(valid_words[i:i + words_per_group])

        ass_content = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Default,Arial,{font_size},{base_color},&H000000FF&,{outline_color},&H80000000&,-1,0,0,0,100,100,1,0,1,{outline_w},3,2,60,60,520,1",
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
                        line_parts.append(r"{\c" + highlight_color + r"\b1}" + item["word"] + r"{\r\c" + base_color + r"\b1}")
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
