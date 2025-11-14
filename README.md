<h1 align="center">Bulk YouTube Video Downloader (BYVD) 🚀</h1>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-v0.2-blue.svg">
  <img alt="Maintenance" src="https://img.shields.io/badge/Maintained-Yes-green.svg">
  <a href="https://github.com/TheForgotensoul/Bulk_Youtube_Video_Downloader/blob/main/LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-yellow.svg">
  </a>
  <a href="https://twitter.com/theforgotensoul">
    <img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/theforgotensoul.svg?style=social">
  </a>
</p>

<p align="center">
  <b>Bulk YouTube Video Downloader (BYVD)</b> is a powerful Python-based tool that downloads 
  <b>high-quality YouTube videos in bulk</b> using CSV input.  
  Supports both a beautiful <b>GUI Application</b> and a fast <b>CLI Mode</b>.
</p>

---

## ✨ Features

✔️ Bulk download unlimited videos  
✔️ Highest-quality video + audio merge (FFmpeg)  
✔️ Clean GUI built using **Flet**  
✔️ Multi-CSV support  
✔️ Real-time progress indicators  
✔️ CLI script for Linux & Windows  
✔️ Sanitized filenames  
✔️ Parallel safe UI updates  
✔️ Automatic temporary file cleanup  

---

## 📦 Installation

You can use **either the GUI App** or the **CLI version**.

---

# 🖥️ **GUI Application (Windows)**

### 1️⃣ Download the latest release  
👉 https://github.com/TheForgotensoul/Bulk_Youtube_Video_Downloader/releases

### 2️⃣ Extract the zip file

### 3️⃣ Run  
```
BYVD.exe
```

### 4️⃣ Load CSV files  
Click **Browse CSVs** → Select the folder containing one or multiple CSV files.

### 5️⃣ Choose output folder  
Select where videos should be saved.

### 6️⃣ Click **Download All**  
Enjoy watching BYVD handle everything automatically.

### 📂 Output  
Videos are saved inside your selected folder in subfolders matching CSV names.

---

# 🛠️ FFmpeg Requirement

BYVD uses **FFmpeg** to merge high-quality video + audio.

### ✔️ No Installation Needed (FFmpeg Included)

You do **NOT** need to download FFmpeg manually.

- The repository already includes an `ffmpeg` folder  
- The Windows release (**BYVD.zip**) already bundles `ffmpeg.exe` together with the application  
- The app automatically uses the included FFmpeg binary


### Linux
```sh
sudo apt install ffmpeg
```

---

# 🧪 CLI Version (Windows / Linux)

### Clone the repository
```sh
git clone https://github.com/TheForgotensoul/Bulk_Youtube_Video_Downloader.git
cd Bulk_Youtube_Video_Downloader
```

### Install dependencies
```sh
pip install -r requirements.txt
```

### FFmpeg for CLI (Windows)
- You do NOT need to install FFmpeg manually.
- The repository already includes an ffmpeg folder ffmpeg.exe is bundled inside the project
- The CLI script automatically uses the included FFmpeg binary

### FFmpeg for CLI (Linux)
#### Linux users need to install FFmpeg because .exe binaries don’t work on Linux:
```sh
sudo apt install ffmpeg
```
---

# 📄 CSV Format

Your CSV **must contain the following exact headers**:

```
Title, Video Link
```

Example:

| Title               | Video Link                 |
|--------------------|-----------------------------|
| My Video Title 1   | https://youtube.com/...     |
| My Video Title 2   | https://youtu.be/...        |

📌 **Do not change header names**  
📌 BYVD supports multiple CSV files in a folder  
📌 Subfolders are created based on CSV filenames  

---

# ▶️ Running CLI Downloader

```sh
python CLI.py
```

### It will ask:

```
Location of CSV files:
Location to save videos:
```

Then it will automatically:

- Read all CSV files  
- Download highest-quality video & audio  
- Merge them using FFmpeg  
- Save inside the selected folder  
- Clean temp files  

---

# 👤 Author

**theforgotensoul**

- Twitter: https://twitter.com/theforgotensoul  
- GitHub: https://github.com/theforgotensoul  

---

# 🤝 Contributing

Contributions, issues and feature requests are welcome!  
👉 https://github.com/TheForgotensoul/Bulk_Youtube_Video_Downloader/issues

---

# ⭐ Support

If this project helped you, please **give it a star!**

---

# 📝 License

This project is licensed under the **MIT License**.
