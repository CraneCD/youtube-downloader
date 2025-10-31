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
        st.caption("MP3 conversion & video merging available")
    else:
        st.warning("⚠️ FFmpeg not found")
        st.caption("Some videos require FFmpeg to merge streams")
        with st.expander("📥 Install FFmpeg for full compatibility"):
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
            
            Note: Many modern YouTube videos require FFmpeg to merge video and audio streams.
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
                                # Without FFmpeg, download in native format
                                ydl_opts.update({
                                    'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                                })
                        else:
                            # Video download options
                            if not has_ffmpeg:
                                # First, inspect available formats and find ones with both video and audio
                                ydl_check = yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True})
                                with ydl_check:
                                    try:
                                        format_info = ydl_check.extract_info(url, download=False)
                                        formats = format_info.get('formats', [])
                                        
                                        # Find formats that have BOTH video and audio codecs (complete files)
                                        complete_formats = []
                                        for fmt in formats:
                                            vcodec = fmt.get('vcodec', 'none')
                                            acodec = fmt.get('acodec', 'none')
                                            # Must have both video AND audio (not "none")
                                            if vcodec and vcodec != 'none' and acodec and acodec != 'none':
                                                complete_formats.append(fmt)
                                        
                                        if complete_formats:
                                            # Filter to ONLY WebM formats
                                            webm_formats = [f for f in complete_formats if f.get('ext', '').lower() == 'webm']
                                            
                                            if not webm_formats:
                                                st.error("❌ No WebM format available for this video.")
                                                st.info("This video doesn't have a complete WebM format. Try a different video or install FFmpeg to merge streams.")
                                                st.stop()
                                            
                                            # Sort by resolution
                                            webm_formats.sort(key=lambda x: (
                                                -x.get('height', 0) if x.get('height') else 0,  # Higher resolution first
                                            ))
                                            
                                            # Filter by quality if specified
                                            if video_quality not in ["Best", "Worst"]:
                                                target_height = int(video_quality.replace('p', ''))
                                                matching = [f for f in webm_formats 
                                                          if f.get('height') and int(str(f.get('height')).replace('p', '')) <= target_height]
                                                if matching:
                                                    webm_formats = matching
                                            
                                            if video_quality == "Worst":
                                                webm_formats.reverse()
                                            
                                            # Use the best matching format
                                            selected = webm_formats[0]
                                            ydl_opts['format'] = selected['format_id']
                                        else:
                                            # No complete formats available - this video needs FFmpeg
                                            st.error("❌ This video only has separate video and audio streams.")
                                            st.warning("🔧 **FFmpeg is REQUIRED** to merge them into a playable file.")
                                            st.info("""
                                            **Please install FFmpeg:**
                                            - Windows: `winget install ffmpeg` or download from ffmpeg.org
                                            - macOS: `brew install ffmpeg`
                                            - Linux: `sudo apt install ffmpeg`
                                            
                                            Then restart the app and try again.
                                            """)
                                            st.stop()
                                    except Exception as e:
                                        st.error(f"❌ Error checking formats: {str(e)}")
                                        st.info("Trying WebM-only format selection...")
                                        # Only WebM formats, no fallback
                                        quality_map = {
                                            "Best": "best[ext=webm]",
                                            "1080p": "best[height<=1080][ext=webm]",
                                            "720p": "best[height<=720][ext=webm]",
                                            "480p": "best[height<=480][ext=webm]",
                                            "360p": "best[height<=360][ext=webm]",
                                            "Worst": "worst[ext=webm]",
                                        }
                                        ydl_opts['format'] = quality_map.get(video_quality, "best[ext=webm]")
                                
                                ydl_opts['prefer_free_formats'] = False
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
                        format_info_text = ""
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            title = info.get('title', 'video')
                            duration = info.get('duration', 0)
                            
                            # Get the format that was actually used
                            format_id = info.get('format_id', 'unknown')
                            format_ext = info.get('ext', 'unknown')
                            vcodec = info.get('vcodec', 'unknown')
                            acodec = info.get('acodec', 'unknown')
                            
                            # Store format info for display
                            format_info_text = f"Format: {format_id}, Container: {format_ext}"
                            if vcodec != 'unknown' and vcodec != 'none':
                                format_info_text += f", Video: {vcodec.split('.')[0]}"
                            if acodec != 'unknown' and acodec != 'none':
                                format_info_text += f", Audio: {acodec.split('.')[0]}"
                        
                        # Find the downloaded file(s)
                        downloaded_files = list(Path(tmpdir).glob('*'))
                        
                        # Filter out .part files (incomplete downloads)
                        downloaded_files = [f for f in downloaded_files if not f.name.endswith('.part')]
                        
                        if downloaded_files:
                            # Check if multiple files were downloaded (video + audio separate)
                            if len(downloaded_files) > 1:
                                st.error("❌ Multiple files downloaded - video and audio are separate!")
                                st.warning("🔧 **FFmpeg is REQUIRED** to merge them into a playable file.")
                                st.info("""
                                **Please install FFmpeg and try again.**
                                - Windows: `winget install ffmpeg`
                                - macOS: `brew install ffmpeg`
                                - Linux: `sudo apt install ffmpeg`
                                """)
                                st.stop()
                            
                            file_path = downloaded_files[0]
                            
                            # Validate file has both video and audio (if it's a video download)
                            if download_format == "Video (MP4)":
                                # Check if file is likely incomplete
                                file_size = file_path.stat().st_size
                                if file_size < 1024:  # Less than 1KB - probably broken
                                    st.error("❌ Downloaded file is too small - download may have failed")
                                    st.stop()
                            
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
                                # Video MIME type mapping
                                video_mime_map = {
                                    '.mp4': 'video/mp4',
                                    '.webm': 'video/webm',
                                    '.mkv': 'video/x-matroska',
                                    '.flv': 'video/x-flv',
                                }
                                mime_type = video_mime_map.get(file_ext, 'video/webm')
                                extension = file_ext.lstrip('.') or 'webm'
                            
                            # Provide download button
                            if download_format == "Audio only":
                                format_label = f"Audio ({extension.upper()})"
                                if has_ffmpeg and extension == 'mp3':
                                    format_label = "Audio (MP3)"
                            else:
                                format_label = "Video (WebM)"
                            
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
                            if format_info_text:
                                st.caption(f"ℹ️ {format_info_text}")
                            
                            # Validation message
                            if download_format == "Video (MP4)" and not has_ffmpeg:
                                if vcodec == 'none' or acodec == 'none':
                                    st.error("⚠️ WARNING: Downloaded file is missing video or audio track!")
                                    st.info("This file may not play correctly. Please install FFmpeg for complete downloads.")
                                else:
                                    st.success("✅ File verified: Contains both video and audio")
                            
                        else:
                            st.error("❌ File not found after download")
                            
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error downloading: {error_msg}")
                
                # Provide helpful error messages for common issues
                if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                    st.warning("🔧 **FFmpeg error**")
                    st.info("""
                    FFmpeg is required for this video. Please install it:
                    - Windows: `winget install ffmpeg`
                    - macOS: `brew install ffmpeg`
                    - Linux: `sudo apt install ffmpeg`
                    """)
                elif "format" in error_msg.lower() or "no video" in error_msg.lower() or "webm" in error_msg.lower():
                    st.warning("⚠️ **No WebM format available**")
                    st.info("""
                    This video doesn't have a complete WebM format available.
                    Try a different video or install FFmpeg to merge video and audio streams.
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
