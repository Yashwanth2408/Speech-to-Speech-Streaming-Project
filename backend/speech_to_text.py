import whisper
import os
import sys
import json

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    millisec = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{millisec:03d}"

def save_transcription_as_srt(transcription_data, output_file="transcription.srt"):
    """
    Saves the transcription in SRT subtitle format.
    
    Parameters:
    transcription_data: Can be either string or dict with segments
    output_file: Path where to save the SRT file
    """
    with open(output_file, "w", encoding="utf-8") as f:
        # Check if we have segments (properly structured data from Whisper)
        if isinstance(transcription_data, dict) and "segments" in transcription_data:
            # Use Whisper's segments with actual timestamps 
            for i, segment in enumerate(transcription_data["segments"], start=1):
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        else:
            # Fallback for string input (not ideal but works as a backup)
            lines = transcription_data.split(". ")
            counter = 1
            timestamp = 0
            for line in lines:
                if line.strip():
                    f.write(f"{counter}\n")
                    # Simple timestamp logic - not ideal but works as fallback
                    f.write(f"00:00:{timestamp:02d},000 --> 00:00:{timestamp+4:02d},000\n")
                    f.write(line.strip() + ".\n\n")
                    timestamp += 5  # Longer time gap
                    counter += 1
    return output_file

def transcribe_audio(audio_path):
    """
    Transcribes the given audio file using Whisper.
    
    Parameters:
    audio_path (str): Path to the audio file
    
    Returns:
    str: Transcribed text
    str: Subtitle file path (if subtitles are enabled)
    dict: Raw transcription result with segments
    """
    try:
        print("⏳ Loading Whisper model... (This may take a few seconds)")
        model = whisper.load_model("small", download_root="venv/")  # Ensure it downloads in venv
        print("✅ Model loaded. Starting transcription...")

        # Run transcription with word timestamps
        result = model.transcribe(audio_path, language="en", word_timestamps=True)
        
        # Get full text
        transcribed_text = result["text"]
        print("\n🎤 Transcription:\n")
        print(transcribed_text)  # Print to console

        # Save full transcription result to JSON for debugging
        json_path = os.path.splitext(audio_path)[0] + "_transcription.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Generate SRT with accurate timestamps
        srt_file = save_transcription_as_srt(result, os.path.splitext(audio_path)[0] + ".srt")
        
        return transcribed_text, srt_file, result

    except Exception as e:
        print(f"❌ Error in transcription: {e}")
        return None, None, None

if __name__ == "__main__":
    audio_file = input("Enter the path of the audio file: ").strip()

    if not os.path.exists(audio_file):
        print("❌ Error: File not found! Please check the path.")
        sys.exit(1)

    transcript, srt_file, _ = transcribe_audio(audio_file)

    if transcript:
        text_output = os.path.splitext(audio_file)[0] + "_transcription.txt"

        with open(text_output, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"\n✅ Transcription saved to: {text_output}")
        print(f"✅ Subtitles saved to: {srt_file}")