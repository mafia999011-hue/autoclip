import os
import uuid
import threading
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from werkzeug.utils import secure_filename
from autoclip.pipeline import AutoClipPipeline
from autoclip.youtube import download_youtube_video

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.expanduser("~/autoclip/uploads")
app.config["OUTPUT_FOLDER"] = os.path.expanduser("~/autoclip/output")
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB max

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

# In-memory session task tracking
tasks = {}
api_key_store = {"key": os.environ.get("GEMINI_API_KEY", "")}

@app.route("/")
def index():
    return render_template("index.html", has_key=bool(api_key_store["key"]))

@app.route("/api/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        data = request.json or {}
        key = data.get("api_key", "").strip()
        api_key_store["key"] = key
        return jsonify({"status": "ok", "has_key": bool(key)})
    return jsonify({"has_key": bool(api_key_store["key"])})

@app.route("/api/youtube", methods=["POST"])
def fetch_youtube():
    data = request.json or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No YouTube URL provided"}), 400
    try:
        res = download_youtube_video(url, app.config["UPLOAD_FOLDER"])
        return jsonify({
            "status": "ready",
            "video_id": res["video_id"],
            "title": res["title"],
            "duration": res["duration"]
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
