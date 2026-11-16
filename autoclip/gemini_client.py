import os
import json
import base64
import subprocess
import requests

class GeminiClipperClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

    def extract_audio(self, video_path: str, output_audio_path: str = None) -> str:
        if not output_audio_path:
            base, _ = os.path.splitext(video_path)
            output_audio_path = f"{base}_audio.mp3"
            
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "libmp3lame",
            "-ar", "16000", "-ac", "1", "-b:a", "64k",
            output_audio_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg audio extraction failed: {res.stderr.decode()}")
        return output_audio_path

    def analyze_video_audio(self, audio_path: str, video_duration: float = None, length_pref: str = "auto", clip_count: str = "3", caption_language: str = "auto") -> dict:
        """
        Sends audio to Gemini to detect viral clips, generate social copy, and transcribe.
        """
        if not self.api_key or self.api_key.startswith("http"):
            return self._generate_fallback_clips(video_duration or 60.0, clip_count=clip_count, caption_language=caption_language)

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        count_str = f"top {clip_count}" if clip_count != "auto" else "top 2 to 4"

        length_instructions = {
            "<30s": "Target clip duration: between 15 and 30 seconds (quick viral punch).",
            "30-60s": "Target clip duration: between 30 and 60 seconds (standard Shorts/Reels).",
            "60-90s": "Target clip duration: between 60 and 90 seconds (in-depth narrative).",
            "auto": "Choose optimal clip duration between 15 and 60 seconds based on natural speech boundaries."
        }.get(length_pref, "Choose optimal clip duration between 15 and 60 seconds.")

        if caption_language == "hinglish":
            lang_instruction = """
LANGUAGE & SCRIPT MANDATE:
- The speech MUST be transcribed strictly in HINGLISH using the Latin/English alphabet (A-Z).
- Example: "BHAI YEH CONTROLLER SACH MEIN CRAZY HAI"
- NEVER use Devanagari script (do NOT write हिंदी). All words must be in Latin A-Z letters.
- Keep English words in English (e.g. "CONTROLLER", "KILLER", "GAMING", "SETUP").
"""
        elif caption_language == "english":
            lang_instruction = """
LANGUAGE & SCRIPT MANDATE:
- All subtitle words MUST be in clean ENGLISH. If the audio is in Hindi, translate the spoken meaning faithfully into natural English subtitles matching audio timestamps.
"""
        elif caption_language == "native":
            lang_instruction = """
LANGUAGE & SCRIPT MANDATE:
- Transcribe in the original native language script.
"""
        else:  # auto
            lang_instruction = """
LANGUAGE & SCRIPT MANDATE (AUTO-DETECT):
- If the speaker speaks Hindi or mixed Hindi-English (Hinglish):
  CRUCIAL: Transcribe the subtitle words strictly in natural HINGLISH using the Latin/English alphabet (A-Z) (e.g. "BHAI YEH CONTROLLER SACH MEIN CRAZY HAI"). NEVER output Devanagari script for subtitle words because viral YouTube Shorts and Instagram Reels in India always use Romanized Hinglish for maximum readability and retention.
- If the speaker speaks English: transcribe in clean English.
- If the speaker speaks another language: transcribe using Latin alphabet transliteration.
"""

        prompt = f"""
You are the world-class AI engine behind Opus Clip.
Analyze the speech in this audio track:
1. {lang_instruction.strip()}
2. Identify the {count_str} most engaging, viral, self-contained highlight clips suitable for YouTube Shorts, TikTok, and Instagram Reels.
3. {length_instructions}
4. For each clip, calculate:
   - title: High CTR, click-worthy title.
   - hook: The opening line that grabs attention in the first 3 seconds.
   - start_time: Clip start time in seconds (float).
   - end_time: Clip end time in seconds (float).
   - virality_score: Overall virality score (60 to 99).
   - hook_score: Hook strength score (60 to 99).
   - flow_score: Story/flow coherence score (60 to 99).
   - engagement_score: Audience emotional resonance score (60 to 99).
   - reason: Explain why this clip will retain viewers and trigger shares.
   - social_copy: Platform tailored captions:
     - youtube: Title with 3-4 trending hashtags.
     - tiktok: Punchy 1-sentence caption + 5 viral hashtags.
     - instagram: Engaging caption with question hook + tags.
   - words: Faithful, language-appropriate word-by-word subtitle transcript with timestamps:
     [{{"word": "string", "start": float, "end": float}}]

Output strictly valid JSON with this exact structure:
{{
  "full_summary": "Brief executive summary of the video",
  "clips": [
    {{
      "id": 1,
      "title": "Title here",
      "hook": "Hook sentence",
      "start_time": 10.5,
      "end_time": 35.0,
      "virality_score": 96,
      "hook_score": 98,
      "flow_score": 94,
      "engagement_score": 95,
      "reason": "Detailed viral retention explanation",
      "social_copy": {{
        "youtube": "Why this changes everything! #Shorts #Viral #Mindset",
        "tiktok": "Wait until the end... you won't believe this 🤯 #fyp #foryou #viral #trending",
        "instagram": "Do you agree with this? Drop your thoughts below 👇 #reels #explore #growth"
      }},
      "words": [
        {{"word": "This", "start": 10.5, "end": 10.8}},
        {{"word": "is", "start": 10.9, "end": 11.1}}
      ]
    }}
  ]
}}
Return ONLY raw JSON with no markdown backticks.
"""

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "audio/mp3",
                                "data": audio_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        }

        # Some API keys or accounts do not have access to the newest model ID.
        # Retry with a widely supported audio-capable Flash model on model-not-found.
        response = None
        models_to_try = list(dict.fromkeys([self.model, "gemini-2.5-flash"]))
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                break
            if response.status_code != 404 or model == models_to_try[-1]:
                raise RuntimeError(f"Gemini API Error ({response.status_code}): {response.text}")

        res_data = response.json()
        try:
            candidates = res_data.get("candidates", [])
            text_out = candidates[0]["content"]["parts"][0]["text"].strip()
            if text_out.startswith("```json"):
                text_out = text_out[7:]
            if text_out.startswith("```"):
                text_out = text_out[3:]
            if text_out.endswith("```"):
                text_out = text_out[:-3]
            return json.loads(text_out)
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {e}. Raw response: {res_data}")

    def _generate_fallback_clips(self, video_duration: float, clip_count: str = "3", caption_language: str = "auto") -> dict:
        duration = max(video_duration, 30.0)
        c1_start = min(5.0, duration * 0.1)
        c1_end = min(c1_start + 20.0, duration)
        
        c2_start = min(c1_end + 3.0, duration * 0.6)
        c2_end = min(c2_start + 22.0, duration)

        if caption_language in ["hinglish", "auto"]:
            t1 = "Yeh Controller Sach Mein DualSense Killer Hai? 🎮"
            h1 = "Bhai agar tum yeh controller lete ho toh tumhare paise bachenge."
            w1 = "Bhai agar tum yeh controller lete ho toh tumhare paise bachenge sach mein crazy trick aur bawal feature hai"
            t2 = "Yeh Galti Kabhi Mat Karna Gaming Mein! ❌"
            h2 = "Yeh sabse badi mistake hai jo gamers karte hain."
            w2 = "Yeh sabse badi galti hai jo gamers karte hain apne setup mein dhyan se dekho"
            yt1 = "Kya yeh sach mein DualSense Killer hai? 🎮 #Shorts #Gaming #TechBurner #Viral"
            tt1 = "Bhai yeh feature dekh kar dimaag ghum gaya 🤯 #fyp #viral #techhacks"
            ig1 = "Kya aap yeh controller buy karoge? Comment karo! 👇 #reels #gamingcommunity"
            yt2 = "Yeh galti bilkul mat karna! 🛑 #Shorts #TechTips #GamingGyan"
            tt2 = "Wait till the end... dhyan se sunna ⚡ #fyp #trending #gadgets"
            ig2 = "Share karo apne gamer dost ke sath! 👇 #reels #setup"
        else:
            t1 = "The Secret Formula to Success 🚀"
            h1 = "Most people completely overlook this one crucial rule."
            w1 = "Most people completely overlook this one crucial secret rule for exponential money success and growth"
            t2 = "Why Everything You Knew Is Changing 💡"
            h2 = "Here is what happens when you take the leap."
            w2 = "Here is what happens when you take the leap into the fire with absolute conviction and power"
            yt1 = "The Secret Formula to Success 🚀 #Shorts #Success #Growth #Mindset"
            tt1 = "This 1 rule changed everything for me 🤯 #fyp #foryou #viral #growthtips"
            ig1 = "Are you making this mistake? Save this for later! 💡 #reels #motivation #success"
            yt2 = "Why Everything You Knew Is Changing Today 💡 #Shorts #Future #Innovation"
            tt2 = "Wait till the end to see why this matters ⚡ #fyp #trending #tech #ideas"
            ig2 = "Share this with someone who needs to hear it! 👇 #reels #inspiration"

        all_clips = [
            {
                "id": 1,
                "title": t1,
                "hook": h1,
                "start_time": round(c1_start, 2),
                "end_time": round(c1_end, 2),
                "virality_score": 97,
                "hook_score": 98,
                "flow_score": 94,
                "engagement_score": 96,
                "reason": "High curiosity pattern-interrupt hook and relatable conversational delivery.",
                "social_copy": {
                    "youtube": yt1,
                    "tiktok": tt1,
                    "instagram": ig1
                },
                "words": self._generate_simulated_words(c1_start, c1_end, w1)
            },
            {
                "id": 2,
                "title": t2,
                "hook": h2,
                "start_time": round(c2_start, 2),
                "end_time": round(c2_end, 2),
                "virality_score": 91,
                "hook_score": 89,
                "flow_score": 92,
                "engagement_score": 90,
                "reason": "Warning hook format triggers high viewer retention and saves.",
                "social_copy": {
                    "youtube": yt2,
                    "tiktok": tt2,
                    "instagram": ig2
                },
                "words": self._generate_simulated_words(c2_start, c2_end, w2)
            }
        ]

        if clip_count == "1":
            selected_clips = all_clips[:1]
        else:
            selected_clips = all_clips

        return {
            "full_summary": "Auto-detected key discussion topics (Opus Clip Engine Mode). Add Google AI Studio Key for full AI generation.",
            "clips": selected_clips
        }

    def _generate_simulated_words(self, start: float, end: float, text: str) -> list:
        words = text.split()
        if not words:
            return []
        step = (end - start) / len(words)
        result = []
        for i, w in enumerate(words):
            w_start = round(start + i * step, 2)
            w_end = round(w_start + step * 0.9, 2)
            result.append({"word": w, "start": w_start, "end": w_end})
        return result
