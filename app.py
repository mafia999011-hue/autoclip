import os
import json
import uuid
import threading
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from werkzeug.utils import secure_filename
from autoclip.pipeline import AutoClipPipeline
from autoclip.downloader import download_online_video
from autoclip.storage import HistoryStorage

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.expanduser("~/autoclip/uploads")
app.config["OUTPUT_FOLDER"] = os.path.expanduser("~/autoclip/output")
app.config["DATA_FOLDER"] = os.path.expanduser("~/autoclip/data")
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB max

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
os.makedirs(app.config["DATA_FOLDER"], exist_ok=True)

history_storage = HistoryStorage(os.path.join(app.config["DATA_FOLDER"], "history.json"))
CONFIG_FILE = os.path.join(app.config["DATA_FOLDER"], "config.json")

def load_saved_key() -> str:
    # 1. Environment variable
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ.get("GEMINI_API_KEY").strip()
    # 2. Config file
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("api_key", "").strip()
        except Exception:
            pass
    return ""

def save_persistent_key(key: str):
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    data["api_key"] = key.strip()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

api_key_store = {"key": load_saved_key()}
tasks = {}

@app.route("/")
def index():
    return render_template("index.html", has_key=bool(api_key_store["key"]))

@app.route("/history")
def history_page():
    return render_template("history.html")

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(history_storage.get_all_clips())

@app.route("/api/history/<filename>", methods=["DELETE"])
def delete_history_clip(filename):
    success = history_storage.delete_clip(filename, output_dir=app.config["OUTPUT_FOLDER"])
    return jsonify({"status": "deleted" if success else "failed"})

@app.route("/api/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        data = request.json or {}
        key = data.get("api_key", "").strip()
        if key.startswith("http://") or key.startswith("https://") or "youtu" in key:
            return jsonify({"status": "error", "error": "API key cannot be a URL", "has_key": False}), 400
        api_key_store["key"] = key
        save_persistent_key(key)
        return jsonify({
            "status": "ok",
            "has_key": bool(key),
            "masked_key": f"{key[:4]}...{key[-4:]}" if len(key) > 8 else ("✓ Set" if key else "")
        })
    
    current_key = api_key_store["key"]
    if current_key.startswith("http"):
        current_key = ""
        api_key_store["key"] = ""

    return jsonify({
        "has_key": bool(current_key),
        "masked_key": f"{current_key[:4]}...{current_key[-4:]}" if len(current_key) > 8 else ("✓ Set" if current_key else "")
    })

@app.route("/api/fetch_url", methods=["POST"])
@app.route("/api/youtube", methods=["POST"])
def fetch_online_video():
    data = request.json or {}
    url = data.get("url", "").strip()
    live_duration = int(data.get("live_duration", 180))
    if not url:
        return jsonify({"error": "No video link provided"}), 400
    try:
        res = download_online_video(url, app.config["UPLOAD_FOLDER"], live_duration=live_duration)
        return jsonify({
            "status": "ready",
            "video_id": res["video_id"],
            "title": res["title"],
            "duration": res["duration"],
            "platform": res.get("platform", "Video")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(filepath)

    return jsonify({
        "status": "uploaded",
        "video_id": unique_name,
        "filename": filename
    })

@app.route("/api/process", methods=["POST"])
def process():
    data = request.json or {}
    video_id = data.get("video_id")
    reframe_mode = data.get("reframe_mode", "blurred_background")
    subtitle_preset = data.get("subtitle_preset", "hormozi")
    enable_emojis = data.get("enable_emojis", True)
    length_pref = data.get("length_pref", "auto")
    clip_count = data.get("clip_count", "3")
    caption_language = data.get("caption_language", "auto")
    video_quality = data.get("video_quality", "1080p")
    show_hook_header = data.get("show_hook_header", True)

    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400

    video_path = os.path.join(app.config["UPLOAD_FOLDER"], video_id)
    if not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"}), 404

    task_id = uuid.uuid4().hex[:8]
    tasks[task_id] = {
        "status": "processing",
        "progress": 5,
        "message": "Initializing Opus Clip AI pipeline...",
        "result": None,
        "error": None
    }

    def run_worker():
        try:
            def update_progress(msg, pct):
                tasks[task_id]["message"] = msg
                tasks[task_id]["progress"] = pct

            pipeline = AutoClipPipeline(
                api_key=api_key_store["key"],
                output_dir=app.config["OUTPUT_FOLDER"]
            )
            result = pipeline.process_video(
                video_path=video_path,
                reframe_mode=reframe_mode,
                subtitle_preset=subtitle_preset,
                enable_emojis=enable_emojis,
                length_pref=length_pref,
                clip_count=clip_count,
                caption_language=caption_language,
                video_quality=video_quality,
                show_hook_header=show_hook_header,
                progress_callback=update_progress
            )
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["progress"] = 100
            tasks[task_id]["result"] = result
        except Exception as e:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = str(e)

    thread = threading.Thread(target=run_worker)
    thread.daemon = True
    thread.start()

    return jsonify({"task_id": task_id, "status": "started"})

@app.route("/api/status/<task_id>")
def status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route("/stream/<filename>")
def stream_video(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, mimetype="video/mp4")

@app.route("/download/<filename>")
def download_clip(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
