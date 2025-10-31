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

**FFmpeg is REQUIRED for most videos to work correctly on Streamlit Cloud!**

#### Option 1: Using `packages.txt` (Easiest - Recommended)

1. **The `packages.txt` file is already in the repo** - it lists FFmpeg as a system dependency
2. When deploying to Streamlit Cloud:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Streamlit Cloud will automatically detect `packages.txt` and install FFmpeg
   - Deploy!

That's it! Streamlit Cloud will install FFmpeg automatically from `packages.txt`.

#### Option 2: Using Dockerfile (Alternative)

If `packages.txt` doesn't work, the repo also includes a `Dockerfile` that installs FFmpeg:

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

**To use the Dockerfile:**
1. In Streamlit Cloud deployment settings, enable "Advanced settings"
2. Select "Use Dockerfile" instead of standard deployment
3. Streamlit Cloud will build using the Dockerfile and FFmpeg will be available

#### Verifying FFmpeg Installation on Streamlit Cloud

After deployment, the app will automatically check for FFmpeg. You should see:
- ✅ "FFmpeg is installed" in the sidebar
- Videos will download and play correctly
- Audio can be converted to MP3

#### Troubleshooting Streamlit Cloud

**If FFmpeg still isn't detected:**
1. Check the deployment logs in Streamlit Cloud
2. Make sure `packages.txt` is in the root of your repo (it should be)
3. Try using the Dockerfile option instead
4. Restart the app after deployment

**Note:** Without FFmpeg on Streamlit Cloud, most modern YouTube videos won't download correctly because they use DASH streaming (separate video/audio streams that need merging).

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
