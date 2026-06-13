import yt_dlp
import os
import shutil

def download_youtube_video(youtube_url, output_dir="downloads"):
    """
    Downloads a YouTube video and saves it as an MP4 file.

    Args:
        youtube_url (str): The URL of the YouTube video or short.
        output_dir (str, optional): Directory to save downloaded files.

    Returns:
        dict: Paths to the downloaded video and extracted audio.
    """
    os.makedirs(output_dir, exist_ok=True)

    video_temp = "youtube_video.mp4"
    audio_temp = "youtube_audio.wav"

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Download best video + best audio
        'outtmpl': os.path.join(output_dir, video_temp),  # Save in output directory
        'merge_output_format': 'mp4',  # Ensure MP4 format
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        final_video_path = os.path.join(output_dir, video_temp)

        print("✅ YouTube Video Downloaded Successfully!")
        return {"video_path": final_video_path}

    except Exception as e:
        print(f"❌ Error downloading YouTube video: {e}")
        return None
