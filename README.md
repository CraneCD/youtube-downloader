# YouTube Downloader Streamlit App

A simple and user-friendly YouTube downloader built with Streamlit and yt-dlp.

## Features

- 📥 Download videos in various qualities (1080p, 720p, 480p, 360p)
- 🎵 Download audio only (MP3 format)
- 🔍 Get video information before downloading
- 📋 Display video details (title, duration, views, thumbnail)

## Installation

### Quick Start - Run Locally (Windows)

**Easiest way:**
1. Double-click `run_local.bat` - it will set everything up automatically!

Or run in PowerShell:
```powershell
.\run_local.ps1
```

The script will:
- ✅ Check Python installation
- ✅ Create a virtual environment (if needed)
- ✅ Install all dependencies
- ✅ Launch the app in your browser

### Manual Local Installation

1. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
   - **Windows (Command Prompt):**
     ```bash
     venv\Scripts\activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

5. **Install FFmpeg** (Required for most videos):

   **Windows:**
   - Option 1 (Recommended): Use winget
     ```powershell
     winget install ffmpeg
     ```
   - Option 2: Download from [FFmpeg website](https://ffmpeg.org/download.html)
     - Download the Windows build
     - Extract the ZIP file
     - Add the `bin` folder to your system PATH

   **macOS:**
   ```bash
   brew install ffmpeg
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **Verify installation:**
   ```bash
   ffmpeg -version
   ```

6. **Run the Streamlit app**:
```bash
streamlit run youtube_downloader_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

### Troubleshooting Local Setup

**Python not found:**
- Make sure Python is installed and added to PATH
- Try `python --version` in your terminal to verify

**Virtual environment issues (PowerShell):**
If you get execution policy errors, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port already in use:**
If port 8501 is busy, Streamlit will use the next available port (8502, 8503, etc.)

### Streamlit Cloud Deployment

**Important:** Streamlit Cloud has limitations with FFmpeg:

1. **FFmpeg is NOT pre-installed** on Streamlit Cloud
2. You have two options:

   **Option A: Use without FFmpeg** (Limited)
   - App will work but many videos won't download as complete files
   - Only videos with existing complete formats will work
   - Audio downloads will be in original format (not MP3)

   **Option B: Use Dockerfile** (Recommended for FFmpeg support)
   - Create a `Dockerfile` in your repo root:
   ```dockerfile
   FROM python:3.11-slim

   RUN apt-get update && apt-get install -y \
       ffmpeg \
       && rm -rf /var/lib/apt/lists/*

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   CMD ["streamlit", "run", "youtube_downloader_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```
   
   - Streamlit Cloud will use this Dockerfile and FFmpeg will be available

## Usage

1. Open the app in your browser (usually at `http://localhost:8501`)
2. Paste a YouTube URL in the input field
3. Optionally click "Get Video Info" to preview video details
4. Select your preferred format (Video MP4 or Audio MP3)
5. If downloading video, choose the quality
6. Click "Download" to start the download
7. Click the download button that appears to save the file to your computer

## Notes

- Please respect copyright and YouTube's Terms of Service
- Some videos may be restricted and cannot be downloaded
- The app downloads files to a temporary directory and provides them for download through the browser
- **For best results, install FFmpeg locally** - it's required to merge video and audio streams from modern YouTube videos

## Troubleshooting

### Videos won't play after download
1. **Install FFmpeg** - Most modern videos require it
2. Try VLC Media Player - it supports the widest range of codecs
3. Check that the file has both video and audio tracks (shown in the app after download)

### FFmpeg not found
- Verify FFmpeg is installed: `ffmpeg -version`
- Make sure FFmpeg is in your system PATH
- Restart your terminal/IDE after installing
- Restart the Streamlit app

## License

MIT
