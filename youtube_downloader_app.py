import streamlit as st
import yt_dlp
import os
import tempfile
from pathlib import Path

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="📥",
    layout="wide"
)

st.title("📥 YouTube Downloader")
st.markdown("Download videos or audio from YouTube")

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
                st.error(f"❌ Error downloading: {str(e)}")
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

