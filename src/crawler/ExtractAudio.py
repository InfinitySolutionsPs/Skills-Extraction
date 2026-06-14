from pathlib import Path
import subprocess

VIDEO_DIR = Path("math_videos")
AUDIO_DIR = Path("math_audio")

AUDIO_DIR.mkdir(exist_ok=True)

video_extensions = [".mp4", ".mkv", ".webm", ".avi", ".mov"]

videos = [
    file for file in VIDEO_DIR.iterdir()
    if file.suffix.lower() in video_extensions
]

print(f"Found {len(videos)} videos")

for video in videos:
    output_audio = AUDIO_DIR / f"{video.stem}.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", str(video),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_audio)
    ]

    print(f"Extracting audio from: {video.name}")

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("Audio extraction completed.")