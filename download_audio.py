import yt_dlp
import os

def download_audio(url, video_id, output_directory):
    output_path = os.path.join(output_directory, f"{video_id}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path
    except Exception as e:
        raise RuntimeError(f"Error downloading video: {str(e)}")
