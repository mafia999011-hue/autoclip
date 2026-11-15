import os
import subprocess

def create_sample_video(output_path="sample_podcast.mp4", duration=30):
    """
    Generates a synthetic 16:9 MP4 test video with visual timer and audio beep/tone.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"testsrc=duration={duration}:size=1280x720:rate=30",
        "-f", "lavfi",
        "-i", f"sine=frequency=440:duration={duration}",
        "-vf", "drawtext=text='AutoClip Test Source %{pts\\:hms}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]
    print(f"Creating sample video: {output_path} ({duration}s)...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to create sample video: {res.stderr.decode()}")
    print("Sample video generated successfully!")
    return output_path

if __name__ == "__main__":
    create_sample_video("uploads/sample_podcast.mp4", duration=35)
