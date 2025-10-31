# YouTube Downloader Streamlit App

A simple and user-friendly YouTube downloader built with Streamlit and yt-dlp.

## Features

- 📥 Download videos in various qualities (1080p, 720p, 480p, 360p)
- 🎵 Download audio only (MP3 format)
- 🔍 Get video information before downloading
- 📋 Display video details (title, duration, views, thumbnail)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. **Important**: For audio downloads (MP3), you need to have FFmpeg installed on your system:
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

3. Run the Streamlit app:
```bash
streamlit run youtube_downloader_app.py
```

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

## License

MIT

