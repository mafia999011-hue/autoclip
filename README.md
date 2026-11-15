# ⚡ AutoClip — AI Video Clipper (Opus Clip Alternative)

> Open-source AI pipeline that turns long videos (podcasts, YouTube, streams) into viral 9:16 vertical shorts with AI hook scoring, auto-reframing, dynamic karaoke subtitles, and multi-platform social captions.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Enabled-green)
![Gemini](https://img.shields.io/badge/Powered%20by-Google%20AI%20Studio-purple)

---

## 🌟 Key Features

* **🔥 AI Virality Score™ & Hook Scoring:** Evaluates hook strength, flow, and virality potential (1–100) using Gemini (`gemini-1.5-flash`).
* **✨ AI Auto-Emoji Engine:** Automatically recognizes keywords and injects contextual animated emojis into captions (e.g. 💰, 🔥, 🏆, 🤫, 🧠).
* **🎨 Subtitle Style Presets:**
  * Hormozi Bold Yellow (highest audience retention)
  * MrBeast Neon Green
  * Cyberpunk Cyan & Violet
  * Sunset Vibrant Pink
* **📐 Smart 9:16 Vertical Reframing:** Converts 16:9 horizontal videos to 1080x1920 portrait shorts using blurred background or center speaker crop.
* **📱 Multi-Platform Social Media Captions:** Generates tailored titles, captions, and viral hashtags for **YouTube Shorts**, **TikTok**, and **Instagram Reels** with 1-click clipboard copy.
* **▶️ YouTube Link Downloader:** Paste any YouTube link directly in the dashboard to fetch and clip videos without manual uploads.
* **⏱ Clip Length & Count Controls:** Choose target duration (`<30s`, `30–60s`, `60–90s`, `Auto`) and number of clips (`1`, `3`, `5`, `10`).

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure `ffmpeg` and `python` are installed:
```bash
pkg install ffmpeg python
```

### 2. Installation
Clone the repository and install requirements:
```bash
git clone https://github.com/mafia999011-hue/autoclip.git
cd autoclip
pip install -r requirements.txt
```

### 3. Launch Dashboard
```bash
python3 app.py
```
Open **`http://localhost:5000`** in your browser!

---

## 🔑 AI Key Setup
Get a free API key from [Google AI Studio](https://aistudio.google.com/) and paste it directly into the dashboard header.

---

## 📄 License
MIT License. Feel free to use, modify, and build upon this project.
