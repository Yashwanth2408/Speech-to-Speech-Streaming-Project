import ffmpeg
import os
import torchaudio

def extract_audio(video_path, output_audio_path):
    """
    Extracts audio from a video file and saves it as a WAV file.
    """
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .run(overwrite_output=True, quiet=True)
        )
        print(f"✅ Audio extracted successfully: {output_audio_path}")

        # Apply noise reduction
        cleaned_audio_path = apply_noise_reduction(output_audio_path)

        # Apply silence trimming
        final_audio_path = remove_silence(cleaned_audio_path)
        
        return final_audio_path  # Return final processed audio
    except Exception as e:
        print(f"❌ Error extracting audio: {e}")
        return None

def apply_noise_reduction(audio_path):
    """
    Applies noise reduction using torchaudio's Voice Activity Detection (VAD).
    Saves and returns the cleaned audio file path.
    """
    try:
        waveform, sample_rate = torchaudio.load(audio_path)
        vad = torchaudio.transforms.Vad(sample_rate=sample_rate)
        cleaned_waveform = vad(waveform)

        cleaned_audio_path = os.path.splitext(audio_path)[0] + "_clean.wav"
        torchaudio.save(cleaned_audio_path, cleaned_waveform, sample_rate)

        print(f"🎧 Noise reduction applied: {cleaned_audio_path}")
        return cleaned_audio_path
    except Exception as e:
        print(f"❌ Error applying noise reduction: {e}")
        return audio_path  # If noise reduction fails, return original audio

def remove_silence(audio_path):
    """
    Removes long silent sections from an audio file.
    """
    try:
        waveform, sample_rate = torchaudio.load(audio_path)
        vad = torchaudio.transforms.Vad(sample_rate=sample_rate)
        trimmed_waveform = vad(waveform)

        trimmed_audio_path = os.path.splitext(audio_path)[0] + "_trimmed.wav"
        torchaudio.save(trimmed_audio_path, trimmed_waveform, sample_rate)

        print(f"✂️ Silence removed: {trimmed_audio_path}")
        return trimmed_audio_path
    except Exception as e:
        print(f"❌ Error removing silence: {e}")
        return audio_path  # If silence removal fails, return cleaned audio

if __name__ == "__main__":
    video_file = input("Enter the path of the video file: ").strip()

    if not os.path.exists(video_file):
        print("❌ Error: File not found! Please check the path.")
    else:
        audio_output = os.path.splitext(video_file)[0] + "_audio.wav"  # Save with same name
        processed_audio = extract_audio(video_file, audio_output)  # Use processed audio
