# ⚡ AutoClip — AI Video Clipper (Opus Clip Alternative)

> **Turn long-form videos (podcasts, streams, YouTube videos) into viral 9:16 vertical shorts with AI virality scoring, dynamic karaoke subtitles, auto-emojis, and multi-platform social captions.**

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
- [📁 Project Architecture](#-project-architecture)
- [🛠 Troubleshooting & FAQ](#-troubleshooting--faq)

---

## ✨ Key Features

* **🔥 AI Virality Score™ & Hook Scoring:** Automatically calculates Hook strength (1–100), Narrative flow (1–100), and Engagement score using Google Gemini (`gemini-1.5-flash`).
* **✨ AI Auto-Emoji Engine:** Analyzes spoken keywords and inserts context-aware animated emojis directly into the subtitles (`MONEY` 💰, `FIRE` 🔥, `SUCCESS` 🏆, `SECRET` 🤫, `MIND` 🧠).
* **🎨 4 Creator Subtitle Presets:** Includes *Hormozi Bold Yellow*, *MrBeast Neon Green*, *Cyberpunk Cyan*, and *Sunset Pink*.
* **📐 Smart 9:16 Reframing:** Converts 16:9 widescreen videos to 1080x1920 portrait shorts with blurred background styling or center speaker crop.
* **📱 Multi-Platform Captions:** Generates tailored titles, hashtags, and captions for **YouTube Shorts**, **TikTok**, and **Instagram Reels** with a 1-click copy button.
* **▶️ YouTube Link Downloader:** Paste any YouTube video URL to automatically download and process at up to 1080p.
* **⏱ Clip Duration & Count Controls:** Choose how many clips you want (`1`, `3`, `5`, `10`) and preferred duration (`< 30s`, `30–60s`, `60–90s`, `Auto`).

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

AutoClip uses Google Gemini for transcription and viral highlight detection:

1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google Account.
3. Click **"Get API key"** and create a new key (free tier available).
4. In the AutoClip dashboard header, paste your key into the **"Enter Google AI Studio Key..."** box and click **Save Key**. The status indicator will turn green!

*(Note: AutoClip also includes a simulated demo mode so you can test the UI even before adding your API key!)*

---

## 🎬 How to Use the Web Dashboard

Once started, open your browser and navigate to:
👉 **`http://localhost:5000`** *(or `http://127.0.0.1:5000`)*

```
+--------------------------------------------------------------------------+
|  ⚡ AutoClip                     [ AI Studio Key: ● Active ] [Save Key]   |
+--------------------------------------------------------------------------+
|                                                                          |
|   Turn Long Videos into Viral Shorts                                     |
|                                                                          |
|   [ 📁 Upload Video File ]   [ ▶️ YouTube URL ]                          |
|   +------------------------------------------------------------------+   |
|   | Paste: https://www.youtube.com/watch?v=...     [ Fetch Video ]   |   |
|   +------------------------------------------------------------------+   |
|                                                                          |
|   SETTINGS:                                                              |
|   🎬 Number of Clips: [ 1 Clip / 3 Clips / 5 Clips ]                     |
|   ⏱ Clip Length:     [ 30s - 60s / < 30s / Auto ]                        |
|   🎨 Subtitle Style:  [ 🟡 Hormozi Yellow / 🟢 MrBeast Green ]            |
|   📐 9:16 Framing:    [ ✨ Blurred Background / 🎯 Center Crop ]          |
|   [✓] 🔥 AI Auto-Insert Viral Emojis                                     |
|                                                                          |
|   [ 🚀 GENERATE VIRAL CLIPS ]                                            |
+--------------------------------------------------------------------------+
```

### Step-by-Step Workflow:
1. **Choose Video Source:**
   * **YouTube URL:** Click the **▶️ YouTube URL** tab, paste your link, and click **Fetch Video**.
   * **Local File:** Drag and drop any `.mp4`, `.mov`, or `.mkv` video.
2. **Select Settings:**
   * **Number of Clips:** Select `1 Clip` (fastest), `3 Clips` (recommended), or `5 Clips`.
   * **Target Length:** Set to `< 30s` for rapid-fire hooks or `30s - 60s` for standard shorts.
   * **Subtitle Style:** Pick your favorite aesthetic preset.
3. **Click "Generate Viral Clips":** AutoClip extracts audio, runs AI moment scoring, reframes to 9:16 vertical video, and burns active karaoke subtitles.
4. **Preview & Download:**
   * Watch the short directly in the built-in 9:16 video player.
   * Check the **Virality Score** and hook feedback.
   * Switch between **YouTube**, **TikTok**, and **Instagram** tabs and click **"Copy"** to grab your upload caption and hashtags.
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

## 📁 Project Architecture

```
autoclip/
├── app.py                  # Flask Web server & REST endpoints
├── requirements.txt        # Python package dependencies
├── README.md               # Documentation & setup guide
├── autoclip/
│   ├── gemini_client.py    # Google AI Studio transcription & viral scoring
│   ├── subtitler.py        # Karaoke ASS subtitle engine & auto-emoji injector
│   ├── reframer.py         # 16:9 to 9:16 aspect ratio filter generator
│   ├── renderer.py         # FFmpeg video cut & compositing engine
│   ├── youtube.py          # yt-dlp YouTube stream downloader
│   └── pipeline.py         # Core orchestration pipeline
├── templates/
│   └── index.html          # Modern dark-mode dashboard
└── static/
    ├── css/style.css       # Styling & responsive design
    └── js/app.js           # Client-side reactivity & clip player
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
This project is open-source under the **MIT License**. Feel free to use, modify, and distribute!
