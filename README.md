# YouTube Downloader Streamlit App

A simple and user-friendly YouTube downloader built with Streamlit and yt-dlp.

## Features

- 📥 Download videos in various qualities (1080p, 720p, 480p, 360p)
- 🎵 Download audio only (MP3 format)
- 🔍 Get video information before downloading
- 📋 Display video details (title, duration, views, thumbnail)

## Installation

### Local Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. **Install FFmpeg** (Required for most videos):

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

3. Run the Streamlit app:
```bash
streamlit run youtube_downloader_app.py
```

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
