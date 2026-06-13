import os
import ffmpeg
import whisper
import subprocess
import requests
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_audio(video_path, output_audio_path):
    """Extracts audio from a video file."""
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .run(overwrite_output=True, quiet=True)
        )
        return output_audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path):
    """Transcribes speech to text using Whisper."""
    try:
        model = whisper.load_model("small")
        result = model.transcribe(audio_path, language="en")
        return result["text"]
    except Exception as e:
        print(f"Error in transcription: {e}")
        return None

class ElevenLabsTTS:
    """Handles text-to-speech conversion using ElevenLabs API."""
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required.")
        self.headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": self.api_key}
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default to Bella (English Female)
    
    async def generate_speech(self, text, output_path):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        payload = {"text": text, "model_id": "eleven_monolingual_v1"}
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            else:
                print(f"TTS API Error: {response.text}")
        except Exception as e:
            print(f"Error generating speech: {e}")
        return None

def sync_audio_to_video(video_path, audio_path, output_path):
    """Syncs new audio with the video."""
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-i", audio_path, "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0", output_path, "-y"],
            check=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error in syncing audio: {e}")
        return None

if __name__ == "__main__":
    video_file = input("Enter video path: ").strip()
    if not os.path.exists(video_file):
        print("Error: File not found.")
        exit()
    
    audio_extracted = extract_audio(video_file, "temp_audio.wav")
    if audio_extracted:
        text_transcribed = transcribe_audio(audio_extracted)
        if text_transcribed:
            tts = ElevenLabsTTS()
            audio_tts = asyncio.run(tts.generate_speech(text_transcribed, "output_tts.wav"))
            if audio_tts:
                synced_video = sync_audio_to_video(video_file, audio_tts, "final_output.mp4")
                if synced_video:
                    print(f"✅ Process completed! Final video saved as {synced_video}")
