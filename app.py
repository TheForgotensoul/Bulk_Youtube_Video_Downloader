import PySimpleGUI as sg
import os

action = ""
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

window.close()
