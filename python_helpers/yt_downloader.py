import yt_dlp
from pydub import AudioSegment
import os

def download_audio_from_url(url):
    original_audio = "audio.mp3"
    converted_audio = "audio_16Khz.mp3"
    ydl_opts = {
        "format" : "bestaudio/best",
        "outtmpl" : "audio.%(ext)s",
        "postprocessors" : [
            {
                "key" : "FFmpegExtractAudio",
                "preferredcodec" : "mp3"
            }
        ]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    convert_to_16Khz(original_audio, converted_audio)

    if os.path.exists(original_audio):
        os.remove(original_audio)
        print(f"Cleaned up temporary file: {original_audio}")

def convert_to_16Khz(input_file, output_file):
    audio = AudioSegment.from_mp3(input_file)
    audio = audio.set_frame_rate(16000)
    audio.export(output_file, format="mp3")

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=rbgjYX9n_dA"
    download_audio_from_url(url)