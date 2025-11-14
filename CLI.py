import csv
import shlex
import shutil
import subprocess
from pathlib import Path
from pytubefix import YouTube

# import pytubefix.request
# import requests

# # --- SOCKS5 Proxy Configuration ---
# proxies = {
#     "http": "socks5h://5.183.70.46:1080",
#     "https": "socks5h://5.183.70.46:1080"
# }

# # --- Create a session that uses the proxy ---
# session = requests.Session()
# session.proxies.update(proxies)

# # --- Patch pytubefix to use requests instead of urllib ---
# def patched_get(url, *args, **kwargs):
#     resp = session.get(url, timeout=20)
#     resp.raise_for_status()
#     return resp.text

# pytubefix.request.get = patched_get

# === CONFIGURATION ===
CSV_FOLDER = Path(
    input("Location of CSV files (e.g., C:/Users/YourName/Downloads/): ").strip())
VIDEOS_FOLDER = Path(
    input("Location to save videos (e.g., C:/Users/YourName/Videos/): ").strip())
TEMP_FOLDER = Path("temp/")

# === SETUP DIRECTORIES ===
VIDEOS_FOLDER.mkdir(parents=True, exist_ok=True)
TEMP_FOLDER.mkdir(parents=True, exist_ok=True)

# === COLLECT ALL LINKS AND TITLES FROM CSV FILES ===
links, titles = [], []
for csv_file in CSV_FOLDER.glob("*.csv"):
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = f'{csv_file.stem} {row["Title"]}'.strip()
            link = row["Video Link"].strip()
            titles.append(title)
            links.append(link)
        print(f"📄 Loaded {len(links)} links from {csv_file.name}")

# === DOWNLOAD FUNCTION (HIGHEST QUALITY ONLY) ===


def download_highest_quality(link, title):
    print(f"\n🎬 Downloading highest quality: {title}")

    if "youtube.com/watch?v=" not in link and "youtu.be/" not in link:
        print(f"⚠️ Invalid link for {title}")
        return

    try:
        yt = YouTube(link, use_oauth=False,
                     allow_oauth_cache=True)

        # Get highest video + audio streams
        video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True) \
                                 .order_by("resolution").desc().first()
        audio_stream = yt.streams.filter(
            only_audio=True).order_by("abr").desc().first()

        if not video_stream or not audio_stream:
            print(f"⚠️ No high-quality streams found for: {title}")
            return

        # Download temporary files
        video_path = TEMP_FOLDER / "video.mp4"
        audio_path = TEMP_FOLDER / "audio.mp3"

        print(f"⬇️ Downloading video ({video_stream.resolution})...")
        video_stream.download(output_path=TEMP_FOLDER, filename="video.mp4")

        print(f"⬇️ Downloading audio ({audio_stream.abr})...")
        audio_stream.download(output_path=TEMP_FOLDER, filename="audio.mp3")

        # Merge with ffmpeg
        output_file = VIDEOS_FOLDER / f"{title.replace(' ', '_')}.mp4"
        cmd = f'ffmpeg -y -i "{audio_path}" -i "{video_path}" -c:v copy -c:a aac -loglevel quiet -stats "{output_file}"'
        subprocess.check_call(shlex.split(cmd))

        print(f"✅ Saved highest quality: {output_file}")

    except Exception as e:
        print(f"❌ Error downloading {title}: {e}")

    finally:
        # Clean up temp folder after each file
        if TEMP_FOLDER.exists():
            shutil.rmtree(TEMP_FOLDER)
            TEMP_FOLDER.mkdir(parents=True, exist_ok=True)


# === MAIN EXECUTION ===
for link, title in zip(links, titles):
    download_highest_quality(link, title)

print("\n🎉 All high-quality downloads completed!")
