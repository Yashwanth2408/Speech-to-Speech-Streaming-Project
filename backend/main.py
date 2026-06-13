from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
from fastapi.staticfiles import StaticFiles

from audio_extraction import extract_audio
from speech_to_text import transcribe_audio
from translate_text import translate_text
from text_to_speech import generate_speech
from sync_audio_to_video import sync_audio_to_video

app = FastAPI()
# Mount the uploads directory to serve files
app.mount("/static", StaticFiles(directory="uploads"), name="static")
# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend domain when deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    video_path = UPLOAD_DIR / file.filename
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"message": "Video uploaded successfully!", "video_path": str(video_path)}

@app.post("/process-video/")
async def process_video(video_path: str, target_language: str, voice_gender: str):
    extracted_audio_path = str(UPLOAD_DIR / "extracted_audio.wav")
    extract_audio(video_path, extracted_audio_path)

    transcript = transcribe_audio(extracted_audio_path)
    translated_text = translate_text(transcript, target_language)

    translated_audio_path = str(UPLOAD_DIR / f"translated_audio_{target_language}.mp3")
    generate_speech(translated_text, translated_audio_path, target_language, voice_gender.lower())

    output_video_path = str(UPLOAD_DIR / f"output_video_{target_language}.mp4")
    sync_audio_to_video(video_path, translated_audio_path, output_video_path)

    return {"output_video": output_video_path}

# Run server: uvicorn main:app --reload
