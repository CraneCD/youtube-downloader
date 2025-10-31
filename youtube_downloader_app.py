import streamlit as st
from pytube import YouTube
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
        st.caption("Audio will download in original format (M4A)")
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
        "This app uses pytube to download content from YouTube. "
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
                    yt = YouTube(url)
                    
                    st.success("✅ Video information retrieved!")
                    st.json({
                        "Title": yt.title,
                        "Duration": f"{yt.length // 60}:{yt.length % 60:02d}",
                        "Channel": yt.author,
                        "Views": yt.views,
                        "Publish Date": yt.publish_date.strftime("%Y-%m-%d") if yt.publish_date else "N/A",
                    })
                    
                    st.session_state['video_info'] = {
                        'title': yt.title,
                        'author': yt.author,
                        'length': yt.length,
                        'views': yt.views,
                        'thumbnail': yt.thumbnail_url
                    }
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
                        yt = YouTube(url)
                        title = yt.title
                        duration = yt.length
                        
                        if download_format == "Audio only":
                            # Download audio stream
                            if has_ffmpeg:
                                # pytube doesn't directly support MP3, so we'll download M4A
                                # Users can convert it themselves if needed
                                audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                                if not audio_stream:
                                    audio_stream = yt.streams.filter(only_audio=True).first()
                                
                                if audio_stream:
                                    file_path = audio_stream.download(output_path=tmpdir, filename="audio")
                                    
                                    # Try to convert to MP3 using ffmpeg if available
                                    import subprocess
                                    mp3_path = os.path.join(tmpdir, "audio.mp3")
                                    try:
                                        subprocess.run([
                                            'ffmpeg', '-i', file_path, '-vn', '-acodec', 'libmp3lame', 
                                            '-ab', '192k', '-ar', '44100', '-y', mp3_path
                                        ], check=True, capture_output=True)
                                        file_path = mp3_path
                                        extension = 'mp3'
                                        mime_type = 'audio/mpeg'
                                    except:
                                        # If conversion fails, use original file
                                        extension = audio_stream.subtype
                                        mime_type = 'audio/mp4' if extension == 'm4a' else 'audio/webm'
                                else:
                                    st.error("❌ No audio stream found")
                                    st.stop()
                            else:
                                # Download M4A audio directly
                                audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                                if not audio_stream:
                                    audio_stream = yt.streams.filter(only_audio=True).first()
                                
                                if audio_stream:
                                    file_path = audio_stream.download(output_path=tmpdir, filename="audio")
                                    extension = audio_stream.subtype
                                    mime_type = 'audio/mp4' if extension == 'm4a' else 'audio/webm'
                                else:
                                    st.error("❌ No audio stream found")
                                    st.stop()
                        else:
                            # Download video stream
                            # pytube provides progressive streams (video + audio) and adaptive streams (separate)
                            # We want progressive streams for complete files
                            streams = yt.streams.filter(progressive=True, file_extension='mp4')
                            
                            if not streams:
                                # Fallback to any progressive stream
                                streams = yt.streams.filter(progressive=True)
                            
                            if not streams:
                                st.error("❌ No complete video stream available. This video may require FFmpeg for merging.")
                                st.info("💡 Try installing FFmpeg or selecting a different video.")
                                st.stop()
                            
                            # Filter by quality
                            selected_stream = None
                            if video_quality == "Best":
                                selected_stream = streams.get_highest_resolution()
                            elif video_quality == "Worst":
                                selected_stream = streams.get_lowest_resolution()
                            else:
                                target_height = int(video_quality.replace('p', ''))
                                # Get streams at or below target resolution, sorted by resolution
                                matching_streams = sorted(
                                    [s for s in streams if s.resolution and int(s.resolution.replace('p', '')) <= target_height],
                                    key=lambda s: int(s.resolution.replace('p', '')) if s.resolution else 0,
                                    reverse=True
                                )
                                if matching_streams:
                                    selected_stream = matching_streams[0]
                                else:
                                    selected_stream = streams.get_lowest_resolution()
                            
                            if not selected_stream:
                                selected_stream = streams[0]
                            
                            file_path = selected_stream.download(output_path=tmpdir)
                            extension = 'mp4'
                            mime_type = 'video/mp4'
                            format_info_text = f"Resolution: {selected_stream.resolution}, Format: {selected_stream.subtype}"
                        
                        # Read file
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        
                        # Get file extension from actual file
                        file_ext = Path(file_path).suffix.lower()
                        if file_ext:
                            extension = file_ext.lstrip('.')
                            if extension == 'm4a':
                                mime_type = 'audio/mp4'
                            elif extension == 'mp4':
                                if download_format == "Audio only":
                                    mime_type = 'audio/mp4'
                                else:
                                    mime_type = 'video/mp4'
                            elif extension == 'webm':
                                mime_type = 'audio/webm' if download_format == "Audio only" else 'video/webm'
                        
                        # Provide download button
                        if download_format == "Audio only":
                            format_label = f"Audio ({extension.upper()})"
                            if extension == 'mp3':
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
                        if 'format_info_text' in locals():
                            st.caption(f"ℹ️ {format_info_text}")
                            
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error downloading: {error_msg}")
                st.info("💡 Tip: Make sure the URL is valid and the video is accessible")
                st.exception(e)  # Show full error for debugging
        else:
            st.warning("⚠️ Please enter a YouTube URL")

# Display session state info if available
if 'video_info' in st.session_state:
    with st.expander("📋 Last Retrieved Video Information"):
        info = st.session_state['video_info']
        st.write(f"**Title:** {info.get('title', 'N/A')}")
        st.write(f"**Channel:** {info.get('author', 'N/A')}")
        st.write(f"**Duration:** {info.get('length', 0) // 60}:{info.get('length', 0) % 60:02d}")
        st.write(f"**Views:** {info.get('views', 0):,}")
        if info.get('thumbnail'):
            st.image(info.get('thumbnail'))

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ using Streamlit and pytube"
    "</div>",
    unsafe_allow_html=True
)
