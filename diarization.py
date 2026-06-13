import whisperx
import torch
import gc

def transcribe_audio(audio_file, device="cuda", batch_size=16, compute_type="float16"):
    try:
        print("Loading WhisperX model...")
        model = whisperx.load_model("large-v2", device, compute_type=compute_type)
        
        print("Loading audio file...")
        audio = whisperx.load_audio(audio_file)
        
        print("Transcribing audio...")
        result = model.transcribe(audio, batch_size=batch_size)
        print("Transcription segments (before alignment):", result["segments"])
        
        del model
        gc.collect()
        torch.cuda.empty_cache()
        
        print("Loading alignment model...")
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        
        print("Aligning transcription...")
        aligned_result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
        print("Aligned transcription segments:", aligned_result["segments"])
        
        del model_a
        gc.collect()
        torch.cuda.empty_cache()
        
        return aligned_result
    
    except Exception as e:
        print("Error:", e)
        return None

if __name__ == "__main__":
    audio_path = "audio.wav"
    final_result = transcribe_audio(audio_path)
    if final_result:
        print("Final Transcription Output:", final_result["segments"])
