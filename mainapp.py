import streamlit as st
import os
import tempfile
from pathlib import Path
import asyncio
import sys
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1" 
# Import functions from other Python files
from audio_extraction import extract_audio
from speech_to_text import transcribe_audio
from translate_text import translate_text, LANGUAGE_OPTIONS
from text_to_speech import generate_speech
from sync_audio_to_video import sync_audio_to_video

# Set page configuration
st.set_page_config(
    page_title="Video Language Converter",
    page_icon="🎬",
    layout="wide"
)


# Helper function to run async functions
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def main():
    st.title("🎬 Video Language Converter")
    st.write("Upload a video and convert its audio to a different language!")
    
    # Create temp directory for file processing
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.TemporaryDirectory()
    
    temp_path = Path(st.session_state.temp_dir.name)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        input_video_path = temp_path / "input_video.mp4"
        
        with open(input_video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success("Video uploaded successfully!")
        
        # Display the original video
        st.subheader("Original Video")
        st.video(str(input_video_path))
        
        # Language selection
        st.subheader("Select Target Language")
        target_language = st.selectbox(
            "Choose the language you want to convert the audio to:",
            list(LANGUAGE_OPTIONS.keys())
        )
        
        # Voice selection
        voice_gender = st.radio(
            "Select voice gender:",
            ("Male", "Female"),
            horizontal=True
        )
        
        # Process button
        if st.button("Convert Video"):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Extract audio
            status_text.text("Step 1/5: Extracting audio from video...")
            extracted_audio_path = temp_path / "extracted_audio.wav"
            extract_audio(str(input_video_path), str(extracted_audio_path))
            progress_bar.progress(20)
            
            # Step 2: Transcribe audio
            status_text.text("Step 2/5: Transcribing audio to text...")
            transcript = transcribe_audio(str(extracted_audio_path))
            
            if transcript:
                st.text_area("Original Transcript", transcript, height=100)
                progress_bar.progress(40)
                
                # Step 3: Translate text
                status_text.text(f"Step 3/5: Translating text to {target_language}...")
                translated_text = translate_text(transcript, target_language)
                
                if translated_text:
                    st.text_area(f"Translated Text ({target_language})", translated_text, height=100)
                    progress_bar.progress(60)
                    
                    # Step 4: Generate speech
                    status_text.text(f"Step 4/5: Generating {target_language} speech...")
                    translated_audio_path = temp_path / f"translated_audio_{target_language.lower()}.mp3"
                    audio_path = run_async(generate_speech(
                        translated_text, 
                        str(translated_audio_path), 
                        target_language, 
                        voice_gender.lower()
                    ))
                    
                    if audio_path:
                        # Let user hear the audio
                        st.audio(audio_path)
                        progress_bar.progress(80)
                        
                        # Step 5: Sync audio to video
                        status_text.text("Step 5/5: Creating final video...")
                        output_video_path = temp_path / f"output_video_{target_language.lower()}.mp4"
                        final_video = sync_audio_to_video(
                            str(input_video_path), 
                            str(translated_audio_path), 
                            str(output_video_path)
                        )
                        
                        if final_video:
                            progress_bar.progress(100)
                            status_text.text("✅ Conversion complete!")
                            
                            # Display the final video
                            st.subheader("Converted Video")
                            st.video(str(output_video_path))
                            
                            # Download button
                            with open(output_video_path, "rb") as file:
                                btn = st.download_button(
                                    label=f"Download {target_language} Video",
                                    data=file,
                                    file_name=f"converted_video_{target_language.lower()}.mp4",
                                    mime="video/mp4"
                                )
                        else:
                            st.error("❌ Error creating final video")
                    else:
                        st.error("❌ Error generating speech")
                else:
                    st.error("❌ Error translating text")
            else:
                st.error("❌ Error transcribing audio")

if __name__ == "__main__":
    main()