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
        ["Video (MP4)", "Audio only"],
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
        st.caption("MP3 conversion available")
    else:
        st.info("ℹ️ FFmpeg not found - app works without it!")
        st.caption("Audio will download in original format (M4A/WebM)")
        with st.expander("📥 Optional: Install FFmpeg for MP3 conversion"):
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
            
            Note: FFmpeg enables MP3 conversion. Without it, audio downloads in original format.
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
                        
                        if download_format == "Audio only":
                            # Download best audio format available
                            if has_ffmpeg:
                                # With FFmpeg, we can convert to MP3
                                ydl_opts.update({
                                    'format': 'bestaudio/best',
                                    'postprocessors': [{
                                        'key': 'FFmpegExtractAudio',
                                        'preferredcodec': 'mp3',
                                        'preferredquality': '192',
                                    }],
                                })
                            else:
                                # Without FFmpeg, download in native format (m4a, webm, opus, etc.)
                                ydl_opts.update({
                                    'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
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
                            
                            # Determine MIME type and extension from actual file
                            file_ext = file_path.suffix.lower()
                            if download_format == "Audio only":
                                # Determine MIME type based on actual file extension
                                audio_mime_map = {
                                    '.mp3': 'audio/mpeg',
                                    '.m4a': 'audio/mp4',
                                    '.webm': 'audio/webm',
                                    '.opus': 'audio/ogg',
                                    '.ogg': 'audio/ogg',
                                }
                                mime_type = audio_mime_map.get(file_ext, 'audio/mpeg')
                                extension = file_ext.lstrip('.') or 'mp3'
                            else:
                                mime_type = "video/mp4"
                                extension = file_ext.lstrip('.') or 'mp4'
                            
                            # Provide download button
                            if download_format == "Audio only":
                                format_label = f"Audio ({extension.upper()})"
                                if has_ffmpeg and extension == 'mp3':
                                    format_label = "Audio (MP3)"
                            else:
                                format_label = "Video"
                            
                            st.success("✅ Download complete!")
                            st.download_button(
                                label=f"⬇️ Download {format_label}",
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
                    st.warning("🔧 **An unexpected FFmpeg error occurred**")
                    st.info("""
                    The app should work without FFmpeg. If you're seeing this error:
                    1. Make sure you're using the latest version of the app
                    2. Try downloading again - it should automatically use formats that don't require FFmpeg
                    3. Check the sidebar for optional FFmpeg installation (only needed for MP3 conversion)
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
