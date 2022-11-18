import csv
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from pytube import YouTube

links = []
titles = []

# folder path to find csv files
res = [x for x in Path("CSV Files/").glob('*.csv')]


for i in range(len(res)):
    # opening the CSV file
    with open(res[i], mode='r')as file:
        # reading the CSV file
        csvFile = csv.DictReader(file)

        # displaying the contents of the CSV file
        for lines in csvFile:
            links.append(lines["Video Link"])
            titles.append(lines["Topic Name"])
    file.close()

# funstion to download videos from youtube


def Download(link, title):
    # create a temp folder
    Path('/temp/').mkdir(parents=True, exist_ok=True)

    # check if the string exist in the link
    if "https://www.youtube.com/watch?v=" in link:

        print(f"Downloading Started for Video with title {title.strip()} \n")
        # Ceate Youtube Object
        youtubeObject = YouTube(link)

        try:

            # Youtube maintains Separate video and audio files for high resolution videos
            # download Video in a temp location
            youtubeObject.streams.get_highest_resolution().download(
                output_path="temp/", filename='video.mp4')

            # Download Audio in a temp location
            youtubeObject.streams.filter(abr="160kbps", progressive=False).first(
            ).download(output_path="temp/", filename='audio.mp3')

        except Exception as e:
            print(e)
            print("An error has occurred")
            sys.exit(1)

        # Access the Audio and video file location
        audio = "./temp/audio.mp3"
        video = "./temp/video.mp4"

        # Define the final merged video Location
        filepath = f"Videos/{title.strip().replace(' ','_')}.mp4"

        # Run FFmpeg in cmd to the audio and video format. this method is used as it is the fastest way to merge the files.
        cmd = f'ffmpeg -y -i {audio}  -r 30 -i {video}  -filter:a aresample=async=1 -c:a flac -c:v copy {filepath} -loglevel quiet -stats'
        subprocess.check_call(shlex.split(cmd))

        print(f"{title.strip()} video has been downloaded successfully \n \n")

        # deleting the temp folder
        shutil.rmtree("temp/")

    else:
        print("Invalid URL")


for i in range(len(links)-1):
    Download(links[i], titles[i])
