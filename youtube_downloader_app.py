import streamlit as st
import yt_dlp
import os
import tempfile
import shutil
from pathlib import Path

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="📥",
    layout="wide"
)

st.title("📥 YouTube Downloader")
st.markdown("Download videos or audio from YouTube")

# Check for ffmpeg availability
def check_ffmpeg():
    """Check if ffmpeg is available in the system PATH"""
    return shutil.which('ffmpeg') is not None

has_ffmpeg = check_ffmpeg()

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Download Settings")
    
    download_format = st.radio(
        "Select format:",
        ["Video (MP4)", "Audio only (MP3)"],
        index=0
    )
    
    if download_format == "Video (MP4)":
        video_quality = st.selectbox(
            "Video quality:",
            ["Best", "1080p", "720p", "480p", "360p", "Worst"],
            index=0
        )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    
    # Show ffmpeg status
    if has_ffmpeg:
        st.success("✅ FFmpeg is installed")
    else:
        st.warning("⚠️ FFmpeg not found")
        with st.expander("📥 How to install FFmpeg"):
            st.markdown("""
            **Windows:**
            1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
            2. Extract and add to PATH
            3. Or use: `winget install ffmpeg`
            
            **macOS:**
            ```bash
            brew install ffmpeg
            ```
            
            **Linux:**
            ```bash
            sudo apt install ffmpeg
            ```
            
            Note: Audio downloads (MP3) require FFmpeg.
            """)
    
    st.info(
        "This app uses yt-dlp to download content from YouTube. "
        "Please respect copyright and YouTube's terms of service."
    )

# Main content area
url = st.text_input(
    "Enter YouTube URL:",
    placeholder="https://www.youtube.com/watch?v=...",
    help="Paste the YouTube video URL here"
)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔍 Get Video Info", use_container_width=True):
        if url:
            try:
                with st.spinner("Fetching video information..."):
                    ydl_opts = {'quiet': True, 'no_warnings': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        st.success("✅ Video information retrieved!")
                        st.json({
                            "Title": info.get('title', 'N/A'),
                            "Duration": f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                            "Uploader": info.get('uploader', 'N/A'),
                            "View Count": info.get('view_count', 0),
                            "Upload Date": info.get('upload_date', 'N/A'),
                        })
                        
                        st.session_state['video_info'] = info
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a YouTube URL")

with col2:
    if st.button("📥 Download", type="primary", use_container_width=True):
        if url:
            try:
                with st.spinner("Downloading..."):
                    # Create temporary directory for downloads
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # Configure yt-dlp options
                        ydl_opts = {
                            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                            'quiet': False,
                        }
                        
                        if download_format == "Audio only (MP3)":
                            ydl_opts.update({
                                'format': 'bestaudio/best',
                                'postprocessors': [{
                                    'key': 'FFmpegExtractAudio',
                                    'preferredcodec': 'mp3',
                                    'preferredquality': '192',
                                }],
                            })
                        else:
                            # Video download options
                            # If ffmpeg is not available, use single-file formats that don't require merging
                            if not has_ffmpeg:
                                # Use formats that are already in a container (no merging needed)
                                quality_map = {
                                    "Best": "best[ext=mp4]/best[ext=webm]/best",
                                    "1080p": "best[height<=1080][ext=mp4]/best[height<=1080][ext=webm]/best[height<=1080]",
                                    "720p": "best[height<=720][ext=mp4]/best[height<=720][ext=webm]/best[height<=720]",
                                    "480p": "best[height<=480][ext=mp4]/best[height<=480][ext=webm]/best[height<=480]",
                                    "360p": "best[height<=360][ext=mp4]/best[height<=360][ext=webm]/best[height<=360]",
                                    "Worst": "worst[ext=mp4]/worst[ext=webm]/worst",
                                }
                                ydl_opts['format'] = quality_map.get(video_quality, "best[ext=mp4]/best")
                                # Don't set merge_output_format when using single-file formats
                            else:
                                # With ffmpeg, we can merge best video + best audio
                                quality_map = {
                                    "Best": "bestvideo+bestaudio/best",
                                    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                                    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                                    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                                    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
                                    "Worst": "worstvideo+worstaudio/worst",
                                }
                                ydl_opts['format'] = quality_map.get(video_quality, "bestvideo+bestaudio/best")
                                ydl_opts['merge_output_format'] = 'mp4'
                        
                        # Download
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            title = info.get('title', 'video')
                            duration = info.get('duration', 0)
                        
                        # Find the downloaded file
                        downloaded_files = list(Path(tmpdir).glob('*'))
                        if downloaded_files:
                            file_path = downloaded_files[0]
                            
                            # Read file
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                            
                            # Determine MIME type and extension
                            if download_format == "Audio only (MP3)":
                                mime_type = "audio/mpeg"
                                extension = "mp3"
                            else:
                                mime_type = "video/mp4"
                                extension = "mp4"
                            
                            # Provide download button
                            st.success("✅ Download complete!")
                            st.download_button(
                                label=f"⬇️ Download {download_format}",
                                data=file_data,
                                file_name=f"{title[:50]}.{extension}",
                                mime=mime_type,
                                use_container_width=True
                            )
                            
                            # Display video info
                            st.info(f"📹 **Title:** {title}\n⏱️ **Duration:** {duration // 60}:{duration % 60:02d}")
                        else:
                            st.error("❌ File not found after download")
                            
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error downloading: {error_msg}")
                
                # Provide helpful error messages for common issues
                if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                    st.warning("🔧 **FFmpeg is required for this download**")
                    if download_format == "Audio only (MP3)":
                        st.info("""
                        **To fix this:**
                        1. Install FFmpeg on your system
                        2. Add FFmpeg to your system PATH
                        3. Restart the Streamlit app
                        
                        See the sidebar for installation instructions.
                        """)
                    else:
                        st.info("""
                        **To fix this:**
                        1. Install FFmpeg for better quality options
                        2. Or the app will try to download in formats that don't require FFmpeg
                        3. Check the sidebar for installation instructions
                        """)
                else:
                    st.info("💡 Tip: Make sure the URL is valid and the video is accessible")
        else:
            st.warning("⚠️ Please enter a YouTube URL")

# Display session state info if available
if 'video_info' in st.session_state:
    with st.expander("📋 Last Retrieved Video Information"):
        info = st.session_state['video_info']
        st.write(f"**Title:** {info.get('title', 'N/A')}")
        st.write(f"**Channel:** {info.get('uploader', 'N/A')}")
        st.write(f"**Duration:** {info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}")
        st.write(f"**Views:** {info.get('view_count', 0):,}")
        if info.get('thumbnail'):
            st.image(info.get('thumbnail'))

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ using Streamlit and yt-dlp"
    "</div>",
    unsafe_allow_html=True
)

