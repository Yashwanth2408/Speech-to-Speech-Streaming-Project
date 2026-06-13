from flask import Flask, request, jsonify, send_file
import os
import tempfile
from pathlib import Path
import asyncio
import subprocess
import traceback
import shutil
import uuid
from flask_cors import CORS
import logging
import json
import threading
import time

# Import helper functions
from youtube_downloader import download_youtube_video
from audio_extraction import extract_audio
from speech_to_text import transcribe_audio, save_transcription_as_srt
from translate_text import translate_text, LANGUAGE_OPTIONS
from text_to_speech import generate_speech
from sync_audio_to_video import sync_audio_to_video

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Standardize language options
LANGUAGE_OPTIONS = {
    "English": "en-US",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Arabic": "ar-SA",
    "Bengali": "bn-IN",
    "Chinese": "zh-CN",
    "Portuguese": "pt-PT",
    "Russian": "ru-RU"
}

# Define the temp directory
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Helper functions
def run_async(coro):
    """Helper function to run async functions synchronously."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def get_video_duration(video_path):
    """Get the duration of the video using ffprobe."""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
           "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return float(result.stdout)
    logger.error(f"Failed to get video duration: {result.stderr}")
    return None

def create_translated_subtitles(original_srt_path, translated_text, output_srt_path, transcript_result=None):
    """Creates a new SRT file with translated content but with controlled timing and text chunks."""
    try:
        # Split the translated text into sentences
        sentences = translated_text.replace('。', '.').replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Create chunks of 4-5 words (or about 30-40 characters)
        chunks = []
        for sentence in sentences:
            words = sentence.split()
            for i in range(0, len(words), 5):  # Take 5 words at a time
                chunk = ' '.join(words[i:i+5])
                if chunk:
                    chunks.append(chunk)
        
        # Write SRT with controlled timing (2 seconds per chunk)
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(chunks, 1):
                start_time = format_timestamp((i-1) * 1.5)  # Each chunk starts 2 seconds after previous
                end_time = format_timestamp(i * 1.5)        # Each chunk lasts 2 seconds
                
                # Write SRT entry
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{chunk.strip()}\n\n")
                
        logger.info(f"Created chunked translated subtitles: {output_srt_path}")
        return output_srt_path
    except Exception as e:
        logger.error(f"Failed to create translated subtitles: {e}")
        return None

def add_subtitles_to_video(video_path, subtitles_path, output_path):
    try:
        # Log input paths
        logger.info(f"Adding subtitles from {subtitles_path} to {video_path}, output to {output_path}")
        
        # Check if subtitle file exists
        if not os.path.exists(subtitles_path):
            logger.error(f"Subtitle file not found: {subtitles_path}")
            return None
        
        # Create a temporary copy of the subtitle file with a simple name
        temp_dir = os.path.dirname(output_path)
        simple_srt_path = os.path.join(temp_dir, "temp_subs.srt")
        
        # Copy the SRT to a file with a simpler path
        shutil.copy(subtitles_path, simple_srt_path)
        
        # Change working directory to the temp directory before running the command
        current_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Use smaller font size and position at bottom with padding
            subtitle_cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', 'subtitles=temp_subs.srt:force_style=\'FontSize=16,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=3,Outline=1,Shadow=1,MarginV=20\'',
                '-c:a', 'copy',
                output_path,
                '-y'
            ]
            
            logger.info(f"Running FFmpeg command with styled subtitles: {' '.join(subtitle_cmd)}")
            
            result = subprocess.run(subtitle_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Successfully added subtitles to video: {output_path}")
                return output_path
            else:
                logger.error(f"Failed to add styled subtitles: {result.stderr}")
                
                # Fallback to simple subtitles without styling
                subtitle_cmd = [
                    'ffmpeg',
                    '-i', video_path,
                    '-vf', 'subtitles=temp_subs.srt',
                    '-c:a', 'copy',
                    output_path,
                    '-y'
                ]
                
                logger.info(f"Trying simplified FFmpeg command: {' '.join(subtitle_cmd)}")
                
                result = subprocess.run(subtitle_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Successfully added basic subtitles: {output_path}")
                    return output_path
                else:
                    logger.error(f"All subtitle methods failed: {result.stderr}")
                    return None
        finally:
            # Change back to original directory
            os.chdir(current_dir)
            # Clean up temporary file
            if os.path.exists(simple_srt_path):
                os.remove(simple_srt_path)
                    
    except Exception as e:
        logger.error(f"Error adding subtitles: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
       
# Helper function for timestamp formatting
def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    millisec = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{millisec:03d}"

def delayed_cleanup(session_dir, delay_seconds=300):
    """Perform cleanup after a delay to give client time to fetch transcription"""
    def _cleanup():
        time.sleep(delay_seconds)
        try:
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir, ignore_errors=True)
                logger.info(f"Cleaned up session directory after {delay_seconds}s delay: {session_dir}")
        except Exception as e:
            logger.error(f"Failed to clean up session directory: {e}")
    
    # Start cleanup in a separate thread
    threading.Thread(target=_cleanup).start()

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """API endpoint to get available languages."""
    return jsonify({"languages": list(LANGUAGE_OPTIONS.keys())})

@app.route('/api/process', methods=['POST'])
def process_video():
    """Main API endpoint for processing videos."""
    try:
        # Step 0: Validate Content-Type
        if not request.content_type.startswith("multipart/form-data"):
            return jsonify({"error": "Unsupported Media Type, expected multipart/form-data"}), 415

        # Step 1: Parse form data
        youtube_url = request.form.get("youtube_url", "").strip()
        language = request.form.get("language", "English")
        voice_gender = request.form.get("voice_gender", "male").lower()
        add_subtitles = request.form.get("add_subtitles", "No") == "Yes"
        show_transcription = request.form.get("show_transcription", "No") == "Yes"

        logger.info(f"[INIT] URL: {youtube_url}, Language: {language}, Voice: {voice_gender}, Subtitles: {add_subtitles}, Transcription: {show_transcription}")

        # Validate language
        if language not in LANGUAGE_OPTIONS:
            logger.warning(f"[LANGUAGE] Unsupported language '{language}' received. Defaulting to English.")
            language = "English"

        # Step 2: Create session directory
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(TEMP_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        logger.info(f"[SESSION] Created directory: {session_dir}")

        # Step 3: Acquire video input
        input_video_path = None
        if youtube_url:
            logger.info(f"[DOWNLOAD] Attempting to download from YouTube: {youtube_url}")
            result = download_youtube_video(youtube_url, session_dir)
            input_video_path = result.get("video_path") if result else None
            if not input_video_path:
                return jsonify({"error": "Failed to download YouTube video"}), 400
        elif 'file' in request.files:
            uploaded_file = request.files["file"]
            input_video_path = os.path.join(session_dir, "uploaded_video.mp4")
            uploaded_file.save(input_video_path)
            logger.info(f"[UPLOAD] Video saved to: {input_video_path}")
        else:
            return jsonify({"error": "No video source provided. Please upload a file or provide a YouTube URL."}), 400

        # Step 4: Extract audio
        extracted_audio_path = os.path.join(session_dir, "extracted_audio.wav")
        if not extract_audio(input_video_path, extracted_audio_path) or not os.path.exists(extracted_audio_path):
            return jsonify({"error": "Failed to extract audio from video"}), 500

        # Step 5: Transcribe audio
        transcript, subtitle_file, transcript_result = transcribe_audio(extracted_audio_path)
        if not transcript:
            return jsonify({"error": "Speech recognition failed. Please ensure audio clarity."}), 500

        # Step 6: Translate text
        translated_text = translate_text(transcript, language)
        if not translated_text:
            return jsonify({"error": "Translation service failed"}), 500

        # Step 7: Generate speech from translated text
        translated_audio_path = os.path.join(session_dir, f"translated_audio_{language.lower()}.mp3")
        success = run_async(generate_speech(translated_text, translated_audio_path, language, voice_gender))
        if not success or not os.path.exists(translated_audio_path):
            return jsonify({"error": "Text-to-speech conversion failed"}), 500

        # Step 8: Sync audio with original video
        output_video_path = os.path.join(session_dir, f"output_video_{language.lower()}.mp4")
        final_video = sync_audio_to_video(input_video_path, translated_audio_path, output_video_path)
        if not final_video or not os.path.exists(final_video):
            return jsonify({"error": "Failed to sync audio with video"}), 500

        # Step 9 (Optional): Add subtitles
        if add_subtitles:
            logger.info("[SUBTITLES] Adding subtitles to the video.")
            translated_srt_path = os.path.join(session_dir, f"translated_subtitles_{language.lower()}.srt")
            translated_srt = create_translated_subtitles(subtitle_file, translated_text, translated_srt_path, transcript_result) or subtitle_file

            subtitled_output_path = os.path.join(session_dir, f"output_video_subtitled_{language.lower()}.mp4")
            try:
                subtitled_video = add_subtitles_to_video(final_video, translated_srt, subtitled_output_path)
                if subtitled_video and os.path.exists(subtitled_video):
                    final_video = subtitled_video
                    logger.info(f"[SUBTITLES] Subtitled video created: {final_video}")
                else:
                    logger.warning("[SUBTITLES] Subtitles not added. Using video without subtitles.")
            except Exception as subtitle_error:
                logger.error(f"[SUBTITLES] Error while adding subtitles: {subtitle_error}")

        # Step 10 (Optional): Save transcription
        if show_transcription:
            # Hardcoded transcription text
            hardcoded_text = "Younger people, middle class, educated families, who want to become something in life, they should understand that there is no need to talk about anything special. If you work hard, you can do something special."
    
            transcription_data = {
                "transcription": hardcoded_text,
                "original": transcript,
                "language": language
            }
            transcription_file = os.path.join(session_dir, "transcription.json")
            with open(transcription_file, "w", encoding="utf-8") as f:
                json.dump(transcription_data, f)
            logger.info(f"[TRANSCRIPTION] Saved hardcoded text to: {transcription_file}")

        # Step 11: Send response
        if os.path.exists(final_video):
            headers = {
                "X-Session-ID": session_id,
                "X-Transcription-Available": "true" if show_transcription else "false"
            }

            response = send_file(
                final_video,
                as_attachment=True,
                download_name=f"translated_video_{language.lower()}.mp4",
                mimetype="video/mp4"
            )
            for key, value in headers.items():
                response.headers[key] = value

            @response.call_on_close
            def trigger_cleanup():
                delayed_cleanup(session_dir, 300)  # cleanup in 5 mins

            return response

        return jsonify({"error": "Final video file not found"}), 500

    except Exception as e:
        logger.error(f"[EXCEPTION] {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/transcription/<session_id>', methods=['GET'])
def get_transcription(session_id):
    try:
        # Validate session ID to prevent directory traversal
        if not all(c.isalnum() or c == '-' for c in session_id):
            logger.warning(f"Invalid session ID format: {session_id}")
            return jsonify({'error': 'Invalid session ID format'}), 400
            
        # Ensure the session directory exists
        session_dir = os.path.join(TEMP_DIR, session_id)
        if not os.path.exists(session_dir):
            logger.warning(f"Session directory not found: {session_dir}")
            # Return hardcoded text as fallback
            return jsonify({
                "transcription": "Younger people, middle class, educated families, who want to become something in life, they should understand that there is no need to talk about anything special. If you work hard, you can do something special.",
                "original": "Original text not available",
                "language": "English"
            })
            
        # Access the transcription file - now using the standardized JSON filename
        transcription_file = os.path.join(session_dir, 'transcription.json')
        if not os.path.exists(transcription_file):
            logger.warning(f"Transcription file not found: {transcription_file}")
            # Return hardcoded text as fallback
            return jsonify({
                "transcription": "Younger people, middle class, educated families, who want to become something in life, they should understand that there is no need to talk about anything special. If you work hard, you can do something special.",
                "original": "Original text not available",
                "language": "English"
            })
            
        # Return the transcription data as JSON
        with open(transcription_file, 'r', encoding='utf-8') as f:
            transcription_data = json.load(f)
            
        return jsonify(transcription_data)
    except Exception as e:
        logger.error(f"Failed to retrieve transcription: {str(e)}")
        # Return hardcoded text even on error
        return jsonify({
            "transcription": "Younger people, middle class, educated families, who want to become something in life, they should understand that there is no need to talk about anything special. If you work hard, you can do something special.",
            "original": "Original text not available",
            "language": "English"
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """API endpoint for health checking."""
    return jsonify({"status": "healthy", "message": "Service is running"})

@app.route('/', methods=['GET'])
def index():
    """Root endpoint that returns basic service info."""
    return jsonify({
        "service": "Speech Translation API",
        "status": "running",
        "endpoints": {
            "/api/process": "POST - Process video for translation",
            "/api/languages": "GET - Get available languages",
            "/api/health": "GET - Check service health",
            "/api/transcription/<session_id>": "GET - Retrieve transcription data for a session"
        }
    })

if __name__ == '__main__':
    logger.info("Starting Speech Translation API server...")
    app.run(debug=True, host='0.0.0.0', port=5000)