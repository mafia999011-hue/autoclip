# ⚡ AutoClip — AI Video Clipper (Opus Clip Alternative)

> **Turn long-form videos (podcasts, streams, YouTube videos) into viral 9:16 vertical shorts with AI virality scoring, millisecond-accurate karaoke subtitles, active word bounce, auto-emojis, and multi-platform social captions.**

[![GitHub Repo](https://img.shields.io/badge/GitHub-mafia999011--hue%2Fautoclip-blue?logo=github)](https://github.com/mafia999011-hue/autoclip)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen?logo=python)](https://python.org)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Hardware%20Accelerated-orange?logo=ffmpeg)](https://ffmpeg.org)
[![Powered by](https://img.shields.io/badge/Powered%20by-Google%20AI%20Studio-blueviolet?logo=google)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents
- [✨ Key Features](#-key-features)
- [📋 System Requirements](#-system-requirements)
- [🚀 Quick Start Guide](#-quick-start-guide)
  - [1. Termux (Android)](#1-termux-android)
  - [2. Linux / Ubuntu](#2-linux--ubuntu)
  - [3. macOS](#3-macos)
  - [4. Windows](#4-windows)
- [🔑 Getting a Free Google AI Studio Key](#-getting-a-free-google-ai-studio-key)
- [🎬 How to Use the Web Dashboard](#-how-to-use-the-web-dashboard)
- [🎨 Subtitle Styles & Presets](#-subtitle-styles--presets)
- [📺 Video Quality Profiles](#-video-quality-profiles)
- [📁 Project Architecture](#-project-architecture)
- [🛠 Troubleshooting & FAQ](#-troubleshooting--faq)
- [📄 License](#-license)

---

## ✨ Key Features

* **🔥 AI Virality Score™ & Hook Scoring:** Evaluates hook strength (1–100), narrative flow (1–100), and emotional engagement using Google Gemini AI.
* **🎙️ Two-Phase Voice-Accurate Transcription:**
  - **Phase 1 (Macro):** Discovers high-retention viral moments across the audio timeline.
  - **Phase 2 (Micro):** Extracts the exact audio snippet and transcribes every spoken word with millisecond-level precision matching the speaker's real vocal timing.
* **🇮🇳 Romanized Hinglish Support:** Transcribes Hindi speech into readable Latin alphabet (A-Z) Hinglish without Devanagari script, designed specifically for Indian YouTube Shorts & Instagram Reels.
* **⚡ 2-Word Punchy Subtitle Delivery:** Rapid-fire 2-word groups with active word **115% bounce pop animation** (`\fscx115\fscy115`) for maximum viewer retention.
* **✨ AI Auto-Emoji Engine:** Analyzes spoken keywords and inserts context-aware animated emojis directly into subtitles (`PAISA` 💰, `AAG` 🔥, `JEET` 🏆, `CRAZY` 🤯, `CONTROLLER` 🎮, `SACH` 💯).
* **🎨 4 Creator Subtitle Presets:** Includes *Hormozi Bold Yellow*, *MrBeast Neon Green*, *Cyberpunk Cyan*, and *Sunset Pink*.
* **📺 Video Quality Profiles:** Choose between **1080p Full HD**, **1440p 2K Ultra HD**, and **720p HD** with automatic subtitle font and margin scaling.
* **📐 Smart 9:16 Reframing & Audio Smoothing:** Converts 16:9 widescreen videos to 9:16 portrait shorts with a darkened blurred background, sharpened foreground, and smooth audio fade-ins/outs to eliminate clicks and pops.
* **🔴 Live Stream Capture:** Paste active YouTube or Twitch live stream URLs to capture live snippets (2 to 10 minutes) on the fly.
* **📁 Persistent Library & History:** Easily view, replay, filter, and delete saved clips from the built-in Library page (`/history`).
* **📱 Multi-Platform Social Captions:** Generates tailored titles, hashtags, and captions for **YouTube Shorts**, **TikTok**, and **Instagram Reels** with a 1-click copy button.

---

## 📋 System Requirements

* **Python:** 3.10 or higher
* **FFmpeg:** Installed with `libass` and `libx264` support
* **RAM:** Minimum 2 GB (4 GB recommended)
* **OS:** Android (Termux), Linux, macOS, or Windows

---

## 🚀 Quick Start Guide

### 1. Termux (Android)
```bash
# 1. Update packages and install prerequisites
pkg update && pkg install -y git python ffmpeg

# 2. Clone the repository
git clone https://github.com/mafia999011-hue/autoclip.git
cd autoclip

# 3. Install Python requirements
pip install -r requirements.txt

# 4. Start the Web Dashboard
python3 app.py
```

### 2. Linux / Ubuntu / Debian
```bash
# 1. Install prerequisites
sudo apt update && sudo apt install -y git python3 python3-pip ffmpeg

# 2. Clone and enter repo
git clone https://github.com/mafia999011-hue/autoclip.git
cd autoclip

# 3. Install requirements & start
pip install -r requirements.txt
python3 app.py
```

### 3. macOS
```bash
# 1. Install prerequisites with Homebrew
brew install git python ffmpeg

# 2. Clone repo and run
git clone https://github.com/mafia999011-hue/autoclip.git
cd autoclip
pip3 install -r requirements.txt
python3 app.py
```

### 4. Windows
```powershell
# 1. Ensure Python and FFmpeg are installed and added to PATH
# 2. Clone and run in PowerShell / Command Prompt
git clone https://github.com/mafia999011-hue/autoclip.git
cd autoclip
pip install -r requirements.txt
python app.py
```

---

## 🔑 Getting a Free Google AI Studio Key

AutoClip connects to Google AI Studio for high-speed transcription and viral highlight detection:

1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google Account.
3. Click **"Get API key"** and create a new key (free tier available).
4. In the AutoClip dashboard header, paste your key into the **"Enter Google AI Studio Key..."** box and click **Save Key**. The key is saved locally in `data/config.json`.

---

## 🎬 How to Use the Web Dashboard

Once started, open your browser and navigate to:
👉 **`http://localhost:5000`** *(or `http://127.0.0.1:5000`)*

```
+--------------------------------------------------------------------------+
|  ⚡ AutoClip    [ Studio ] [ Saved Library ]    [ ● Key Active ] [Save]  |
+--------------------------------------------------------------------------+
|                                                                          |
|   Turn Long Videos into Viral Shorts                                     |
|                                                                          |
|   [ 📁 Upload Video File ]   [ 🌐 YouTube & Twitch URL ]                 |
|   +------------------------------------------------------------------+   |
|   | Paste: https://www.youtube.com/watch?v=...     [ Fetch Video ]   |   |
|   +------------------------------------------------------------------+   |
|                                                                          |
|   SETTINGS:                                                              |
|   🎬 Number of Clips:  [ 1 Clip / 3 Clips / 5 Clips ]                    |
|   ⏱ Clip Length:      [ 30s - 60s / < 30s / Auto ]                       |
|   🗣️ Language:         [ ⚡ Auto (Hinglish/English) ]                    |
|   🎨 Subtitle Style:   [ 🟡 Hormozi Yellow / 🟢 MrBeast Green ]           |
|   📺 Video Quality:    [ 💎 1080p Full HD / 👑 2K / ⚡ 720p ]            |
|   📐 9:16 Framing:     [ ✨ Blurred Background / 🎯 Center Crop ]         |
|   [✓] 🔥 AI Auto-Insert Viral Emojis                                    |
|                                                                          |
|   [ 🚀 GENERATE VIRAL CLIPS ]                                            |
+--------------------------------------------------------------------------+
```

### Step-by-Step Workflow:
1. **Choose Video Source:**
   * **YouTube / Twitch URL:** Click the **🌐 YouTube & Twitch URL** tab, paste your link, and click **Fetch Video**. Live stream links are automatically captured as fresh live snippets.
   * **Local File:** Drag and drop any `.mp4`, `.mov`, or `.mkv` video.
2. **Select Settings:**
   * **Number of Clips:** Select `1 Clip` (fastest), `3 Clips` (recommended), or `5 Clips`.
   * **Target Length:** Set to `< 30s` for quick viral hooks or `30s - 60s` for standard shorts.
   * **Video Quality:** Select `1080p Full HD` (recommended), `1440p 2K Ultra HD`, or `720p HD`.
   * **Subtitle Style:** Pick your favorite aesthetic preset.
3. **Click "Generate Viral Clips":** AutoClip extracts audio, runs 2-phase transcription, aligns timestamps to the speaker's voice, reframes to 9:16 vertical video, and burns active karaoke subtitles.
4. **Preview & Download:**
   * Watch the short directly in the built-in 9:16 video player.
   * Check virality score, hook score, flow score, and retention explanation.
   * Switch between **YouTube**, **TikTok**, and **Instagram** tabs and click **"Copy"** to grab your platform-tailored caption and hashtags.
   * Click **⬇️ Download Vertical Short** to save your video!

---

## 🎨 Subtitle Styles & Presets

| Preset | Highlight Color | Outline | Vibe |
|---|---|---|---|
| **Hormozi Bold Yellow** | Neon Yellow (`#FFFF00`) | Solid Black Outline | High-retention, podcast/business |
| **MrBeast Neon Green** | Bright Green (`#00FF00`) | Heavy Stroke | High-energy, challenges, gaming |
| **Cyberpunk Cyan** | Electric Blue (`#00FFFF`) | Deep Violet | Tech, future, AI content |
| **Sunset Pink** | Vibrant Magenta (`#FF00FF`) | Solid Black | Lifestyle, vlog, aesthetic |

---

## 📺 Video Quality Profiles

| Profile | Resolution | Bitrate & Speed | Audio | Best For |
|---|---|---|---|---|
| **💎 1080p Full HD** | 1080 × 1920 | High Bitrate (`CRF 20`, `veryfast`) | 192 kbps | YouTube Shorts, TikTok & Instagram Reels algorithm boost |
| **👑 2K / 1440p Ultra HD** | 1440 × 2560 | Near-Lossless (`CRF 18`, `veryfast`) | 256 kbps | Pristine masters for iPads, tablets, and 4K displays |
| **⚡ 720p HD** | 720 × 1280 | Lightweight (`CRF 23`, `ultrafast`) | 128 kbps | Fast mobile rendering & quick WhatsApp / Discord sharing |

---

## 📁 Project Architecture

```
autoclip/
├── app.py                  # Flask Web server & REST endpoints
├── requirements.txt        # Python package dependencies
├── LICENSE                 # Open-source MIT License
├── README.md               # Documentation & setup guide
├── autoclip/
│   ├── downloader.py       # Universal YouTube & Twitch downloader with bot bypass
│   ├── live_recorder.py    # Live stream HLS capture engine
│   ├── gemini_client.py    # 2-Phase transcription & viral moment scoring
│   ├── subtitler.py        # Karaoke ASS subtitle engine & auto-emoji injector
│   ├── reframer.py         # 16:9 to 9:16 aspect ratio filter generator
│   ├── renderer.py         # FFmpeg video cut, quality profiling & compositing
│   ├── storage.py          # Persistent clip library & history manager
│   └── pipeline.py         # Core orchestration pipeline
├── templates/
│   ├── index.html          # Studio creation dashboard
│   └── history.html        # Saved library & clip player
└── static/
    ├── css/style.css       # Styling & responsive design
    └── js/
        ├── app.js          # Studio reactivity & clip player
        └── history.js      # Library search, filter & player
```

---

## 🛠 Troubleshooting & FAQ

#### 1. Port 5000 is already in use
Run the app on a different port:
```bash
python3 -c "from app import app; app.run(host='0.0.0.0', port=5050)"
```

#### 2. Subtitles are not appearing on the output video
Ensure your FFmpeg build has `libass` enabled:
```bash
ffmpeg -filters | grep ass
```
If missing, reinstall ffmpeg: `pkg install ffmpeg` (Termux) or `sudo apt install ffmpeg libass-dev` (Linux).

#### 3. How to access from another device on the same Wi-Fi?
Look at the terminal output when running `app.py`. It displays your local IP address:
```
* Running on http://192.168.x.x:5000
```
Open that address in any mobile or desktop browser on the same Wi-Fi network!

---

## 📄 License
This project is open-source under the **[MIT License](LICENSE)**. Feel free to use, modify, and distribute!
