import streamlit as st
import yt_dlp
import os
import tempfile
import shutil
import glob
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
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return True
    
    # Also check common installation paths (for Windows)
    import platform
    if platform.system() == 'Windows':
        # Check common fixed paths
        common_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                return True
        
        # Check for any ffmpeg* directory in C:\ and Program Files
        search_patterns = [
            r'C:\ffmpeg*\bin\ffmpeg.exe',
            r'C:\ffmpeg*\ffmpeg.exe',
            r'C:\Program Files\ffmpeg*\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg*\bin\ffmpeg.exe',
        ]
        for pattern in search_patterns:
            for path in glob.glob(pattern):
                if os.path.exists(path):
                    return True
    
    return False

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
    
    # Network settings
    with st.expander("🌐 Network Settings (Advanced)"):
        retry_count = st.slider("Retry attempts on failure:", min_value=3, max_value=20, value=10, help="Number of times to retry if download fails")
        timeout_seconds = st.slider("Connection timeout (seconds):", min_value=30, max_value=300, value=60, help="How long to wait for server response")
        st.caption("Adjust these if you experience timeout errors or have slow internet")
        st.session_state['retry_count'] = retry_count
        st.session_state['timeout_seconds'] = timeout_seconds
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    
    # Show ffmpeg status
    if has_ffmpeg:
        st.success("✅ FFmpeg is installed")
        st.caption("MP3 conversion available")
    else:
        st.error("⚠️ FFmpeg not found - REQUIRED for most videos!")
        st.caption("Modern YouTube videos need FFmpeg to merge video and audio streams")
        
        # Add button to auto-install FFmpeg on Windows
        import platform
        current_os = platform.system()
        
        if current_os == 'Windows':
            st.markdown("---")
            st.markdown("### 📥 Auto-Install FFmpeg")
            install_clicked = st.button("🚀 Install FFmpeg Automatically (Windows)", type="primary", use_container_width=True, key="install_ffmpeg_btn")
            if install_clicked:
                import subprocess
                with st.spinner("Installing FFmpeg via winget..."):
                    try:
                        # Try to install FFmpeg using winget
                        result = subprocess.run(
                            ['winget', 'install', 'ffmpeg', '--silent', '--accept-package-agreements', '--accept-source-agreements'],
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minute timeout
                        )
                        
                        if result.returncode == 0:
                            st.success("✅ FFmpeg installation initiated!")
                            st.info("""
                            **Next steps:**
                            1. The installation may require administrator privileges - check for UAC prompt
                            2. Wait for installation to complete
                            3. Restart this Streamlit app (Ctrl+C and run again)
                            4. FFmpeg should be detected automatically
                            """)
                            st.warning("⚠️ **Important:** You must restart the Streamlit app after installation for FFmpeg to be detected!")
                        else:
                            st.error(f"❌ Installation failed: {result.stderr}")
                            st.info("""
                            **Troubleshooting:**
                            - winget may require administrator privileges
                            - Try running PowerShell as Administrator and run: `winget install ffmpeg`
                            - Or use manual installation (see instructions below)
                            """)
                    except FileNotFoundError:
                        st.error("❌ winget not found!")
                        st.info("""
                        **winget is not available on this system.**
                        
                        **Manual installation required:**
                        1. Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
                        2. Extract and add to PATH
                        3. Restart the app
                        """)
                    except subprocess.TimeoutExpired:
                        st.warning("⏳ Installation is taking longer than expected...")
                        st.info("The installation may still be running. Check for UAC prompts or install manually.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("Try manual installation instead (see instructions below).")
        
        # Add a button to help diagnose
        if st.button("🔍 Check FFmpeg Installation", use_container_width=True, key="check_ffmpeg_btn"):
            import platform
            import subprocess
            st.write("**System Information:**")
            st.write(f"- OS: {platform.system()}")
            st.write(f"- Python: {platform.python_version()}")
            
            # Try to find ffmpeg
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path:
                st.success(f"✅ Found FFmpeg at: {ffmpeg_path}")
                try:
                    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
                    st.code(result.stdout.split('\n')[0])
                except:
                    st.warning("FFmpeg found but couldn't execute - may need PATH update")
            else:
                st.error("❌ FFmpeg not found in PATH")
                # Also check common paths
                if platform.system() == 'Windows':
                    found_paths = []
                    search_patterns = [
                        r'C:\ffmpeg*\bin\ffmpeg.exe',
                        r'C:\ffmpeg*\ffmpeg.exe',
                        r'C:\Program Files\ffmpeg*\bin\ffmpeg.exe',
                        r'C:\Program Files (x86)\ffmpeg*\bin\ffmpeg.exe',
                    ]
                    for pattern in search_patterns:
                        for path in glob.glob(pattern):
                            if os.path.exists(path):
                                found_paths.append(path)
                    
                    if found_paths:
                        st.warning(f"⚠️ FFmpeg found but not in PATH:")
                        for path in found_paths:
                            st.write(f"  - {path}")
                        st.info("Add FFmpeg to your PATH or restart the app - it should auto-detect now.")
                    else:
                        st.info("""
                        **Troubleshooting:**
                        1. Install FFmpeg using the instructions below
                        2. Add FFmpeg to your system PATH
                        3. Restart your terminal/IDE
                        4. Restart the Streamlit app (Ctrl+C and run again)
                        """)
        
        with st.expander("📥 CRITICAL: Install FFmpeg (Required)"):
            st.markdown("""
            ### Windows Installation:
            
            **Method 1: Using the button above (Auto-install)**
            - Click the "📥 Install FFmpeg (Windows)" button above
            - Approve UAC prompt if asked
            - Restart the app after installation
            
            **Method 2: Using winget (Recommended)**
            ```powershell
            winget install ffmpeg
            ```
            Then restart your terminal and Streamlit app.
            
            **Method 3: Manual Installation**
            1. Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
            2. Choose "Windows builds from gyan.dev" or "Essentials build"
            3. Extract the ZIP file (e.g., to `C:\\ffmpeg`)
            4. Add to PATH:
               - Press `Win + X` → System → Advanced System Settings
               - Click "Environment Variables"
               - Under "System Variables", find "Path" and click "Edit"
               - Click "New" and add: `C:\\ffmpeg\\bin` (or wherever you extracted it)
               - Click OK on all dialogs
            5. Restart your terminal/IDE
            6. Verify: Open new terminal and run `ffmpeg -version`
            
            ### macOS Installation:
            ```bash
            brew install ffmpeg
            ```
            
            ### Linux Installation:
            ```bash
            sudo apt update
            sudo apt install ffmpeg
            ```
            
            ### After Installation:
            1. Close and restart your terminal/command prompt
            2. Verify: Run `ffmpeg -version` in a new terminal
            3. Restart this Streamlit app (stop with Ctrl+C, then run again)
            
            **Note:** If FFmpeg still isn't detected after installation, the PATH may not be updated. Try restarting your computer.
            
            **For Streamlit Cloud:** The Dockerfile in the repo will install FFmpeg automatically.
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
                        # Get retry and timeout settings from session state or use defaults
                        retry_count = st.session_state.get('retry_count', 10)
                        timeout_seconds = st.session_state.get('timeout_seconds', 60)
                        
                        # Configure yt-dlp options with timeout and retry settings
                        ydl_opts = {
                            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                            'quiet': False,
                            # Network timeout settings
                            'socket_timeout': timeout_seconds,  # Socket timeout in seconds
                            'retries': retry_count,  # Number of retries for downloads
                            'fragment_retries': retry_count,  # Retries for fragments
                            'file_access_retries': 3,  # Retries for file access
                            # Download settings
                            'external_downloader_args': {
                                'default': [f'--timeout={timeout_seconds}', f'--retries={retry_count}']
                            },
                            # Progress hooks
                            'noprogress': False,
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
                                        # Use format_note to identify progressive/complete streams
                                        complete_formats = []
                                        for fmt in formats:
                                            vcodec = fmt.get('vcodec', 'none')
                                            acodec = fmt.get('acodec', 'none')
                                            format_note = fmt.get('format_note', '').lower()
                                            protocol = fmt.get('protocol', '').lower()
                                            # Must have both video AND audio (not "none")
                                            # Prefer progressive formats or formats that are explicitly complete
                                            # Avoid DASH/manifest formats which are adaptive
                                            if (vcodec and vcodec != 'none' and 
                                                acodec and acodec != 'none' and
                                                'dash' not in protocol and
                                                'manifest' not in protocol):
                                                complete_formats.append(fmt)
                                        
                                        if complete_formats:
                                            # Filter to ONLY MP4 formats (most compatible)
                                            # Also prefer H.264 video codec for maximum compatibility
                                            mp4_formats = [f for f in complete_formats if f.get('ext', '').lower() == 'mp4']
                                            
                                            if not mp4_formats:
                                                st.error("❌ No complete MP4 format available for this video.")
                                                st.info("This video doesn't have a complete MP4 format. Try a different video or install FFmpeg to merge streams.")
                                                st.stop()
                                            
                                            # Sort: prefer H.264 video codec (best compatibility), then by resolution
                                            mp4_formats.sort(key=lambda x: (
                                                'avc' not in x.get('vcodec', '').lower() and 'h264' not in x.get('vcodec', '').lower(),  # H.264 first
                                                -x.get('height', 0) if x.get('height') else 0,  # Higher resolution first
                                            ))
                                            
                                            # Filter by quality if specified
                                            if video_quality not in ["Best", "Worst"]:
                                                target_height = int(video_quality.replace('p', ''))
                                                matching = [f for f in mp4_formats 
                                                          if f.get('height') and int(str(f.get('height')).replace('p', '')) <= target_height]
                                                if matching:
                                                    mp4_formats = matching
                                            
                                            if video_quality == "Worst":
                                                mp4_formats.reverse()
                                            
                                            # Use the best matching format
                                            selected = mp4_formats[0]
                                            ydl_opts['format'] = selected['format_id']
                                            
                                            # Show selected format details for debugging
                                            st.info(f"📋 Selected format: {selected.get('format_id')} | "
                                                  f"Resolution: {selected.get('resolution', 'N/A')} | "
                                                  f"Video: {selected.get('vcodec', 'N/A')[:10]} | "
                                                  f"Audio: {selected.get('acodec', 'N/A')[:10]}")
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
                                        st.info("Trying MP4-only format selection...")
                                        # Only MP4 formats with both video and audio (strict format selector)
                                        # This format selector requires both vcodec and acodec to be present
                                        quality_map = {
                                            "Best": "best[ext=mp4][vcodec*=avc][acodec*=mp4a]/best[ext=mp4][vcodec][acodec]",
                                            "1080p": "best[height<=1080][ext=mp4][vcodec*=avc][acodec*=mp4a]/best[height<=1080][ext=mp4][vcodec][acodec]",
                                            "720p": "best[height<=720][ext=mp4][vcodec*=avc][acodec*=mp4a]/best[height<=720][ext=mp4][vcodec][acodec]",
                                            "480p": "best[height<=480][ext=mp4][vcodec*=avc][acodec*=mp4a]/best[height<=480][ext=mp4][vcodec][acodec]",
                                            "360p": "best[height<=360][ext=mp4][vcodec*=avc][acodec*=mp4a]/best[height<=360][ext=mp4][vcodec][acodec]",
                                            "Worst": "worst[ext=mp4][vcodec][acodec]",
                                        }
                                        ydl_opts['format'] = quality_map.get(video_quality, "best[ext=mp4][vcodec][acodec]")
                                
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
                                mime_type = video_mime_map.get(file_ext, 'video/mp4')
                                extension = file_ext.lstrip('.') or 'mp4'
                            
                            # Provide download button
                            if download_format == "Audio only":
                                format_label = f"Audio ({extension.upper()})"
                                if has_ffmpeg and extension == 'mp3':
                                    format_label = "Audio (MP3)"
                            else:
                                format_label = "Video (MP4)"
                            
                            st.success("✅ Download complete!")
                            st.download_button(
                                label=f"⬇️ Download {format_label}",
                                data=file_data,
                                file_name=f"{title[:50]}.{extension}",
                                mime=mime_type,
                                use_container_width=True
                            )
                            
                            # Display video info
                            file_size_mb = len(file_data) / (1024 * 1024)
                            st.info(f"📹 **Title:** {title}\n⏱️ **Duration:** {duration // 60}:{duration % 60:02d}\n📦 **File Size:** {file_size_mb:.2f} MB")
                            if format_info_text:
                                st.caption(f"ℹ️ {format_info_text}")
                            
                            # Detailed validation and diagnostics
                            if download_format == "Video (MP4)":
                                if vcodec != 'none' and acodec != 'none':
                                    st.success(f"✅ File structure verified: Video ({vcodec.split('.')[0] if vcodec != 'unknown' else 'N/A'}) + Audio ({acodec.split('.')[0] if acodec != 'unknown' else 'N/A'})")
                                    
                                    # Check file size reasonableness
                                    expected_size_mb_per_min = 10  # Rough estimate
                                    expected_size = (duration / 60) * expected_size_mb_per_min
                                    if file_size_mb < expected_size * 0.5:  # Less than 50% of expected
                                        st.warning("⚠️ File size seems unusually small - download may be incomplete or corrupted")
                                else:
                                    st.error("❌ CRITICAL: File is missing video or audio track!")
                                    st.warning("🔧 **FFmpeg is REQUIRED** - this video needs stream merging")
                                
                                # Troubleshooting info
                                with st.expander("🔧 Troubleshooting: File won't play?"):
                                    st.markdown("""
                                    **If the downloaded file won't play:**
                                    1. **Try VLC Media Player** - it supports the widest range of codecs
                                    2. **Check file extension** - Make sure it's `.mp4`
                                    3. **File may be corrupted** - Try downloading again
                                    4. **Install FFmpeg** - Most modern videos require FFmpeg to merge streams properly
                                    
                                    **Recommended solution:** Install FFmpeg for guaranteed playable downloads
                                    """)
                            
                            # Warning if we got multiple files
                            if len(downloaded_files) > 1 and not has_ffmpeg:
                                st.error("❌ Multiple files detected - video and audio are separate!")
                                st.warning("🔧 **FFmpeg is REQUIRED** to merge them into one playable file.")
                        else:
                            st.error("❌ File not found after download")
                            
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error downloading: {error_msg}")
                
                # Provide helpful error messages for common issues
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    st.warning("⏱️ **Network Timeout Error**")
                    st.info("""
                    **The download timed out.** This can happen if:
                    - Your internet connection is slow
                    - YouTube servers are busy
                    - The video file is very large
                    
                    **Solutions:**
                    1. Try downloading again - network issues are often temporary
                    2. Increase timeout in Network Settings (sidebar)
                    3. Increase retry count in Network Settings
                    4. Try downloading at a lower quality (720p or 480p)
                    5. Check your internet connection
                    """)
                elif "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                    st.warning("🔧 **FFmpeg error**")
                    st.info("""
                    FFmpeg is required for this video. Please install it:
                    - Windows: `winget install ffmpeg`
                    - macOS: `brew install ffmpeg`
                    - Linux: `sudo apt install ffmpeg`
                    """)
                elif "format" in error_msg.lower() or "no video" in error_msg.lower() or "mp4" in error_msg.lower():
                    st.warning("⚠️ **No complete MP4 format available**")
                    st.info("""
                    This video doesn't have a complete MP4 format available.
                    Try a different video or install FFmpeg to merge video and audio streams.
                    """)
                elif "connection" in error_msg.lower() or "network" in error_msg.lower() or "httperror" in error_msg.lower():
                    st.warning("🌐 **Network/Connection Error**")
                    st.info("""
                    **Connection problem detected.**
                    
                    **Try:**
                    1. Check your internet connection
                    2. Try again in a few moments
                    3. Increase retry count in Network Settings (sidebar)
                    4. Verify the YouTube URL is correct and accessible
                    """)
                else:
                    st.info("💡 Tip: Make sure the URL is valid and the video is accessible. If problems persist, try adjusting Network Settings in the sidebar.")
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
