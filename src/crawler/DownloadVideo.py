from pathlib import Path
from yt_dlp import YoutubeDL

# =========================================
# PLAYLIST URL
# =========================================
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLPxWrt2xY8992_ukRvgFnPRRgsAuBZQGw"

# =========================================
# OUTPUT DIRECTORY
# =========================================
OUTPUT_DIR = Path("math_videos")
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================================
# KEYWORDS
# =========================================
MATH_KEYWORDS = [
    "رياضيات",
    "الرياضيات",
    "Math",
    "قسمة",
    "جمع",
    "طرح",
    "ضرب",
    "كسور",
    "هندسة",
    "أعداد"
]

# =========================================
# EXTRACT PLAYLIST INFO
# =========================================
extract_opts = {
    "extract_flat": True,
    "quiet": True,
}

print("Reading playlist...")

with YoutubeDL(extract_opts) as ydl:

    playlist_info = ydl.extract_info(
        PLAYLIST_URL,
        download=False
    )

videos_to_download = []

# =========================================
# FILTER VIDEOS
# =========================================
for entry in playlist_info["entries"]:

    if not entry:
        continue

    title = entry.get("title", "")

    if any(keyword.lower() in title.lower() for keyword in MATH_KEYWORDS):

        video_url = f"https://www.youtube.com/watch?v={entry['id']}"

        videos_to_download.append(video_url)

        print(f"Matched: {title}")

print(f"\nTotal math videos found: {len(videos_to_download)}")

# =========================================
# DOWNLOAD VIDEOS
# =========================================
download_opts = {

    "format": "mp4",

    "outtmpl": str(
        OUTPUT_DIR / "%(playlist_index)s - %(title)s.%(ext)s"
    ),

    "ignoreerrors": True,
}

print("\nDownloading videos...")

with YoutubeDL(download_opts) as ydl:

    ydl.download(videos_to_download)

print("\nAll math videos downloaded.")