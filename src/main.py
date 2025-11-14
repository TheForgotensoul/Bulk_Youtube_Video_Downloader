import flet as ft
import csv
import os
import threading
from pytubefix import YouTube
import subprocess
import shlex
import shutil
import tempfile
import re


def main(page: ft.Page):
    page.title = "Bulk YouTube Downloader"
    page.window.icon = "F:/Python_Projects/Bulk_Youtube_Video_Downloader/src/assets/logo.ico"
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.bgcolor = "#0f172a"
    page.window_width = 950
    page.window_height = 750
    page.theme_mode = ft.ThemeMode.DARK

    csv_map = {}
    progress_cards = {}
    downloading = False
    cancel_flag = False

    # ---------------- SAFE UI UPDATE ---------------- #
    def safe_ui_update(func):
        threading.Timer(0, func).start()

    # ---------------- UTILS ---------------- #
    def sanitize_filename(name):
        return re.sub(r'[\\/*?:"<>|]', "_", name)

    # ---------------- ALERT + SNACK HELPERS ---------------- #
    def show_alert(msg, color="#2563eb", icon=ft.Icons.INFO_OUTLINED, title="Notice"):
        def close_dialog(e):
            page.close(dialog)

        if page.platform in [ft.PagePlatform.IOS, ft.PagePlatform.MACOS]:
            dialog = ft.CupertinoAlertDialog(
                title=ft.Text(title, color=color),
                content=ft.Row([ft.Icon(icon, color=color), ft.Text(
                    msg, color="#e2e8f0")], spacing=10),
                actions=[ft.CupertinoDialogAction(
                    "OK", is_default_action=True, on_click=close_dialog)],
            )
        else:
            dialog = ft.AlertDialog(
                title=ft.Text(title, color=color),
                content=ft.Row([ft.Icon(icon, color=color), ft.Text(
                    msg, color="#e2e8f0")], spacing=10),
                actions=[ft.TextButton("OK", on_click=close_dialog)],
            )

        safe_ui_update(lambda: page.open(dialog))

    def show_toast(msg, color="#2563eb", icon=ft.Icons.INFO_OUTLINED, timeout=2):
        snack = ft.SnackBar(
            content=ft.Row(
                [ft.Icon(icon, color=color, size=20),
                 ft.Text(msg, color="#f8fafc", size=14)],
                spacing=10),
            bgcolor="#1e293b",
            duration=timeout * 1000,
            show_close_icon=True,
        )
        page.snack_bar = snack
        snack.open = True
        safe_ui_update(page.update)

    # ---------------- PICKERS ---------------- #
    def on_csv_folder_selected(e: ft.FilePickerResultEvent):
        if e.path:
            csv_folder_input.value = e.path
            load_csvs(e.path)
            page.update()

    def on_download_folder_selected(e: ft.FilePickerResultEvent):
        if e.path:
            download_folder_input.value = e.path
            page.update()

    csv_picker = ft.FilePicker(on_result=on_csv_folder_selected)
    download_picker = ft.FilePicker(on_result=on_download_folder_selected)
    page.overlay.extend([csv_picker, download_picker])

    def select_csv_folder(e):
        csv_picker.get_directory_path(dialog_title="Select CSV Folder")

    def select_download_folder(e):
        download_picker.get_directory_path(
            dialog_title="Select Download Folder")

    def open_download_folder(e):
        folder = download_folder_input.value
        if folder and os.path.exists(folder):
            try:
                os.startfile(folder)
            except Exception:
                show_alert("Unable to open folder.", "#dc2626",
                           ft.Icons.ERROR, title="Error")
        else:
            show_alert("Please select a valid download folder.",
                       "#f59e0b", ft.Icons.FOLDER_OPEN, title="Warning")

    # ---------------- UI ELEMENTS ---------------- #
    csv_folder_input = ft.TextField(
        label="CSV Folder Path", expand=True, read_only=True)
    download_folder_input = ft.TextField(
        label="Download To Folder", expand=True, read_only=True)
    video_list = ft.Column(scroll="auto", expand=True, spacing=8)
    status_text = ft.Text("", size=14, color="#94a3b8")

    preview_dialog = ft.AlertDialog(
        title=ft.Text("CSV Preview"), content=ft.Text(""))

    # ---------------- LOAD CSV ---------------- #
    def load_csvs(folder):
        nonlocal csv_map
        csv_map.clear()
        progress_cards.clear()
        video_list.controls.clear()

        if not folder or not os.path.exists(folder):
            show_alert("Invalid CSV folder.", "#dc2626",
                       ft.Icons.WARNING, title="Error")
            return

        csv_files = [f for f in os.listdir(
            folder) if f.lower().endswith(".csv")]
        if not csv_files:
            show_alert("No CSV files found in this folder.", "#f59e0b",
                       ft.Icons.FOLDER_OFF_OUTLINED, title="Warning")
            return

        total_videos = 0
        for csv_file in csv_files:
            csv_videos = []
            csv_path = os.path.join(folder, csv_file)
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "Video Link" in row and "Title" in row:
                            title = row["Title"].strip()
                            link = row["Video Link"].strip()
                            if link:
                                csv_videos.append((title, link))
                                total_videos += 1
                csv_map[csv_file.split(".")[0]] = csv_videos
            except Exception as e:
                show_alert(f"Error reading {csv_file}: {e}",
                           "#dc2626", ft.Icons.ERROR, title="Error")

        for csv_name, videos in csv_map.items():
            header_row = ft.Row(
                [
                    ft.Text(f"📁 {csv_name}.csv", size=16,
                            color="#60a5fa", weight=ft.FontWeight.BOLD),
                    ft.TextButton("Preview", on_click=lambda e,
                                  n=csv_name: preview_csv(n))
                ],
                alignment="spaceBetween",
            )
            video_list.controls.append(header_row)
            for title, _ in videos:
                pb = ft.ProgressRing(
                    value=0, width=35, height=35, color="#3b82f6", bgcolor="#1e293b")
                pct = ft.Text("0%", size=12, color="#e2e8f0")
                progress_card = ft.Row(
                    [pb, pct, ft.Text(title, color="#e2e8f0", expand=True)],
                    alignment="start",
                    vertical_alignment="center",
                )
                progress_cards[title] = (pb, pct)
                video_list.controls.append(progress_card)

        show_toast(f"✅ Loaded {total_videos} videos from {len(csv_files)} CSVs.",
                   "#16a34a", ft.Icons.CHECK_CIRCLE_OUTLINE)
        page.update()

    # ---------------- CSV PREVIEW ---------------- #
    def preview_csv(csv_name):
        videos = csv_map.get(csv_name, [])
        preview_text = "\n".join(
            [f"{i+1}. {v[0]}" for i, v in enumerate(videos[:5])])
        preview_dialog.content = ft.Text(
            preview_text or "No entries found.", color="#e2e8f0")
        page.dialog = preview_dialog
        preview_dialog.open = True
        page.update()

    # ---------------- DOWNLOAD ---------------- #
    def start_download(e):
        nonlocal downloading, cancel_flag

        if downloading:
            show_toast("⚠️ Download already running.",
                       "#f59e0b", ft.Icons.PAUSE_CIRCLE)
            return
        if not csv_map:
            show_alert("No CSV files loaded.", "#f59e0b",
                       ft.Icons.WARNING, title="Warning")
            return
        if not download_folder_input.value:
            show_alert("Please select a download folder.", "#f59e0b",
                       ft.Icons.FOLDER_OPEN, title="Warning")
            return
        if shutil.which("ffmpeg") is None:
            show_alert("⚠️ FFmpeg not found! Please install it.",
                       "#dc2626", ft.Icons.ERROR, title="Missing Dependency")
            return

        cancel_flag = False
        downloading = True
        start_btn.disabled = True
        cancel_btn.disabled = False
        status_text.value = "🚀 Downloading videos..."
        page.update()

        threading.Thread(target=download_thread, daemon=True).start()

    def cancel_download(e):
        nonlocal cancel_flag
        cancel_flag = True
        cancel_btn.disabled = True
        status_text.value = "🛑 Cancelling downloads..."
        page.update()

    # ---------------- DOWNLOAD THREAD ---------------- #
    def download_thread():
        nonlocal downloading, cancel_flag
        total_downloaded = 0

        for csv_name, videos in csv_map.items():
            subfolder = os.path.join(download_folder_input.value, csv_name)
            os.makedirs(subfolder, exist_ok=True)

            for title, link in videos:
                if cancel_flag:
                    break

                safe_ui_update(lambda: setattr(
                    status_text, 'value', f"📹 Downloading: {title}"))

                try:
                    yt = YouTube(link, on_progress_callback=lambda s,
                                 c, r: on_progress(title, s, c, r))
                    video_stream = yt.streams.filter(
                        adaptive=True, file_extension="mp4", only_video=True).order_by("resolution").desc().first()
                    audio_stream = yt.streams.filter(
                        only_audio=True).order_by("abr").desc().first()

                    if not video_stream or not audio_stream:
                        safe_ui_update(lambda: show_toast(
                            f"No high-quality streams for {title}", "#f59e0b", ft.Icons.WARNING))
                        continue

                    with tempfile.TemporaryDirectory() as temp_dir:
                        video_path = os.path.join(temp_dir, "video.mp4")
                        audio_path = os.path.join(temp_dir, "audio.mp3")
                        video_stream.download(
                            output_path=temp_dir, filename="video.mp4")
                        audio_stream.download(
                            output_path=temp_dir, filename="audio.mp3")

                        output_file = os.path.join(
                            subfolder, f"{sanitize_filename(title)}.mp4")
                        cmd = f'ffmpeg -y -i "{audio_path}" -i "{video_path}" -c:v copy -c:a aac -loglevel quiet "{output_file}"'
                        subprocess.check_call(
                            shlex.split(cmd),
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )

                    total_downloaded += 1
                    safe_ui_update(
                        lambda t=title: update_progress_text(t, 1, done=True))

                except Exception as ex:
                    safe_ui_update(lambda: show_alert(
                        f"❌ Failed {title}: {ex}", "#dc2626", ft.Icons.ERROR, title="Error"))

            if cancel_flag:
                break

        if cancel_flag:
            safe_ui_update(lambda: show_alert(
                "🛑 Downloads cancelled.", "#dc2626", ft.Icons.CANCEL, title="Cancelled"))
        else:
            safe_ui_update(lambda: show_alert(
                f"🎉 All downloads completed! ({total_downloaded} new)", "#16a34a", ft.Icons.CHECK_CIRCLE, title="Success"))

        downloading = False
        safe_ui_update(reset_ui)

    def reset_ui():
        start_btn.disabled = False
        cancel_btn.disabled = True
        status_text.value = ""
        page.update()

    # ---------------- PROGRESS UPDATE ---------------- #
    def on_progress(title, stream, chunk, bytes_remaining):
        total = stream.filesize
        downloaded = total - bytes_remaining
        progress = downloaded / total
        safe_ui_update(lambda: update_progress_text(title, progress))

    def update_progress_text(title, progress, done=False):
        pb, pct = progress_cards.get(title, (None, None))
        if pb and pct:
            pb.value = progress
            pct.value = "✅" if done else f"{int(progress * 100)}%"
        page.update()

    # ---------------- LAYOUT ---------------- #
    start_btn = ft.FilledButton(
        "📥 Download All", on_click=start_download, style=ft.ButtonStyle(bgcolor="#2563eb"))
    cancel_btn = ft.FilledButton("❌ Cancel", on_click=cancel_download, style=ft.ButtonStyle(
        bgcolor="#dc2626"), disabled=True)
    open_btn = ft.FilledButton(
        "📂 Open Folder", on_click=open_download_folder, style=ft.ButtonStyle(bgcolor="#1e40af"))

    page.add(
        ft.Column(
            [
                ft.Text("🎬 Bulk YouTube Downloader", size=22,
                        weight=ft.FontWeight.BOLD, color="#60a5fa"),
                ft.Row([csv_folder_input, ft.ElevatedButton(
                    "📂 Browse CSVs", on_click=select_csv_folder)], spacing=10),
                ft.Row([download_folder_input, ft.ElevatedButton(
                    "📁 Choose Download Folder", on_click=select_download_folder)], spacing=10),
                ft.Row([start_btn, cancel_btn, open_btn], spacing=10),
                ft.Container(video_list, expand=True,
                             bgcolor="#1e293b", border_radius=10, padding=15),
                status_text,
            ],
            expand=True,
            spacing=15,
        )
    )


ft.app(target=main)
