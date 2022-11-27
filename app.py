import csv
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import PySimpleGUI as sg
from pytube import YouTube


def main():
    links = []
    titles = []
    action = ""

    # funstion to download videos from youtube
    def Download(link, title):
        # create a videos folder
        Path('Videos/').mkdir(parents=True, exist_ok=True)
        # create a temp folder
        Path('temp/').mkdir(parents=True, exist_ok=True)

        # check if the string exist in the link
        if "https://www.youtube.com/watch?v=" in link:

            print(
                f"Downloading Started for Video with title {title.strip()} \n")
            window["-action-"].update(f"Downloading Started for Video with title {title.strip()}")
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

            # deleting the temp folder
            shutil.rmtree("temp/")

        else:
            print("Invalid URL")


    file_list_column = [
        [
            sg.Text("CSV Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Text(action, key="-action-"),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(50, 20), key="-FILE LIST-"
            )
        ],
        [
            sg.Button('Exit', button_color=('white', 'firebrick3')),
            sg.Button('Download', button_color=('white', 'green'))
        ],
    ]

    layout = [
        [
            sg.Column(file_list_column)
        ]
    ]

    window = sg.Window("Youtube Video Downloader", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        # Folder name was filled in, make a list of files in the folder
        if event == "-FOLDER-":
            window.refresh()
            window["-action-"].update("CSV Files")
            folder = values["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".csv"))
            ]
            window["-FILE LIST-"].update(fnames)

            for i in fnames:
                n = f"{folder}/{i}"
                # opening the CSV file
                with open(n, mode='r')as file:
  
                    # reading the CSV file
                    csvFile = csv.DictReader(file)

                    # displaying the contents of the CSV file
                    for lines in csvFile:
                        titles.append(f'{i.split(".")[0]}_{lines["Title"]}')
                        links.append(lines["Video Link"])
                file.close()
        elif event == 'Download':
            window.refresh()
            window["-action-"].update("Downloading Videos") 
            try:
                for j in range(len(links)):
                    window["-FILE LIST-"].update(f"Downloading Started for Video with title {titles[j].strip()}")
                    Download(links[j], titles[j])
            except Exception as e:
                print(e)
                print("An error has occurred")
                sys.exit(1)
                
    window.close()
    
if __name__ == '__main__':
    main()