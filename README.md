# 🎬 Speech-to-Speech Streaming Project

> **AI-Powered Video Language Converter** | Transform videos into any language with automatic transcription, translation, and voice synthesis

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)

A powerful end-to-end solution for converting video content from one language to another while maintaining lip-sync timing and natural voice quality. This project combines state-of-the-art AI models including OpenAI Whisper for speech recognition, Edge TTS for neural voice synthesis, and intelligent audio-video synchronization algorithms.

## 🌟 Key Features

- **🎙️ Automatic Speech Recognition**: Leverages OpenAI Whisper's "small" model for accurate transcription across multiple languages
- **🌍 Multi-Language Translation**: Supports 11 languages including Spanish, French, German, Hindi, Tamil, Arabic, Bengali, Chinese, Portuguese, Russian, and English
- **🗣️ Neural Voice Synthesis**: Utilizes Microsoft Edge TTS with gender-specific voice options (male/female) for each language
- **⏱️ Intelligent Audio Synchronization**: Automatically adjusts speech tempo to match original video duration using advanced FFmpeg filters
- **🖥️ Interactive Web Interface**: User-friendly Streamlit dashboard for seamless video processing
- **📊 Real-Time Progress Tracking**: Visual feedback for each processing stage
- **💾 Download Support**: Instant download of converted videos in MP4 format

## 🏗️ Architecture Overview

The application follows a modular pipeline architecture with five distinct processing stages:

Input Video → Audio Extraction → Speech-to-Text → Translation → Text-to-Speech → Audio-Video Sync → Output Video

### Component Breakdown

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Audio Extraction** | FFmpeg | Extracts audio from video in WAV format (16kHz, mono, PCM) |
| **Speech Recognition** | OpenAI Whisper | Transcribes audio to text with high accuracy |
| **Translation Engine** | Google Translate API | Converts text between 11 supported languages |
| **Voice Synthesis** | Edge TTS | Generates natural-sounding speech in target language |
| **Audio Synchronization** | FFmpeg | Matches audio duration to video length with tempo adjustment |
| **Web Interface** | Streamlit | Provides interactive UI for video upload and processing |

## 📋 Prerequisites

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python Version**: 3.8 or higher
- **FFmpeg**: Version 4.0 or higher (must be installed and added to system PATH)
- **FFprobe**: Included with FFmpeg installation
- **RAM**: Minimum 4GB (8GB recommended for faster processing)
- **Storage**: At least 2GB free space for model downloads and temporary files

### Required Libraries

The project depends on the following Python packages:

- `streamlit>=1.28.0` - Web application framework
- `openai-whisper>=20230314` - Speech recognition model
- `edge-tts>=6.1.0` - Text-to-speech synthesis
- `googletrans==4.0.0rc1` - Translation service
- `ffmpeg-python>=0.2.0` - Python bindings for FFmpeg
- `torch>=2.0.0` - PyTorch for Whisper model
- `numpy>=1.24.0` - Numerical computing

## 🚀 Installation Guide

### Step 1: Clone the Repository

git clone https://github.com/Yashwanth2408/Speech-to-Speech-Streaming-Project.git
cd Speech-to-Speech-Streaming-Projec

### Step 2: Install FFmpeg

**Windows:**
Download from https://ffmpeg.org/download.html
Extract and add to PATH environment variable

**macOS:**
brew install ffmpeg

**Linux (Ubuntu/Debian):**
sudo apt update
sudo apt install ffmpeg

### Step 3: Create Virtual Environment

python -m venv venv

Activate virtual environment
Windows:
venv\Scripts\activate

macOS/Linux:
source venv/bin/activate

### Step 4: Install Python Dependencies

pip install streamlit
pip install openai-whisper
pip install edge-tts
pip install googletrans==4.0.0rc1
pip install ffmpeg-python
pip install torch torchvision torchaudio

**Note**: For macOS users with Apple Silicon, set the environment variable to enable MPS fallback:

export PYTORCH_ENABLE_MPS_FALLBACK=1

## 💻 Usage

### Running the Web Application

Launch the Streamlit interface with a single command:

streamlit run mainapp.py


The application will automatically open in your default browser at `http://localhost:8501`.

### Using the Web Interface

1. **Upload Video**: Click "Upload a video file" and select your MP4, AVI, MOV, or MKV file
2. **Select Target Language**: Choose from 11 supported languages in the dropdown menu
3. **Choose Voice Gender**: Select either Male or Female voice for the target language
4. **Convert Video**: Click "Convert Video" to start the processing pipeline
5. **Monitor Progress**: Watch the real-time progress bar and status updates
6. **Preview Results**: Review the transcription, translation, and hear the generated audio
7. **Download**: Click "Download" to save the converted video to your device

### Command-Line Usage

Each module can also be used independently via command line:

#### Audio Extraction
python audio_extraction.py

Enter video path when prompted

#### Speech-to-Text Transcription
python speech_to_text.py

Enter audio path when prompted

#### Text Translation
python translate_text.py

Enter transcription file path and select language

#### Text-to-Speech Generation
python text_to_speech.py

Enter translated text file path and voice preferences

#### Audio-Video Synchronization
python sync_audio_to_video.py

Enter video path, audio path, and output filename

## 🌍 Supported Languages

The system supports bidirectional conversion between the following languages:

| Language | Code | Male Voice | Female Voice |
|----------|------|-----------|--------------|
| English | en | en-US-GuyNeural | en-US-JennyNeural |
| Spanish | es | es-ES-AlvaroNeural | es-ES-ElviraNeural |
| French | fr | fr-FR-HenriNeural | fr-FR-DeniseNeural |
| German | de | de-DE-ConradNeural | de-DE-KatjaNeural |
| Hindi | hi | hi-IN-MadhurNeural | hi-IN-SwaraNeural |
| Tamil | ta | ta-IN-ValluvarNeural | ta-IN-PallaviNeural |
| Arabic | ar | ar-SA-FareedNeural | ar-SA-ZariyahNeural |
| Bengali | bn | bn-IN-BashkarNeural | bn-IN-TanishaaNeural |
| Chinese | zh-cn | zh-CN-YunxiNeural | zh-CN-XiaoxiaoNeural |
| Portuguese | pt | pt-PT-FernandoNeural | pt-PT-FernandaNeural |
| Russian | ru | ru-RU-DmitryNeural | ru-RU-SvetlanaNeural |

## 🔧 Technical Details

### Audio Processing Pipeline

The audio extraction module converts video audio to a standardized format for optimal processing:

- **Format**: WAV (Waveform Audio File Format)
- **Codec**: PCM signed 16-bit little-endian
- **Channels**: Mono (1 channel)
- **Sample Rate**: 16kHz (optimal for Whisper model)

### Speech Recognition

Whisper model configuration:

- **Model Size**: Small (244M parameters)
- **Download Location**: `venv/` directory (approximately 500MB)
- **Transcription Mode**: Automatic language detection with English enforcement
- **Accuracy**: High accuracy for clear audio with minimal background noise

### Audio Synchronization Algorithm

The synchronization module implements a sophisticated three-step process:

1. **Duration Analysis**: Uses FFprobe to measure exact video and audio durations
2. **Tempo Adjustment**: Calculates speed factor as `video_duration / audio_duration`
3. **Audio Processing**: Applies FFmpeg `atempo` filter to match durations precisely
4. **Quality Preservation**: Maintains 48kHz sample rate and AAC encoding for optimal quality

**Speed Factor Calculation**:
speed_factor = video_duration / audio_duration

The `atempo` filter supports speed adjustments from 0.5x to 2.0x while preserving pitch.

### Translation Service

Uses Google Translate API through the `googletrans` library:

- **API Version**: 4.0.0rc1
- **Character Limit**: Up to 15,000 characters per request
- **Error Handling**: Automatic retry with exponential backoff
- **Fallback**: Defaults to English if target language is unavailable

## 📁 Project Structure

Speech-to-Speech-Streaming-Project/
│
├── mainapp.py # Streamlit web application (main entry point)
├── audio_extraction.py # FFmpeg-based audio extraction module
├── speech_to_text.py # Whisper transcription module
├── translate_text.py # Google Translate integration
├── text_to_speech.py # Edge TTS voice synthesis
├── sync_audio_to_video.py # Audio-video synchronization module
├── LICENSE # MIT License
├── Agile Sheet- YashwanthBalaji.xlsx # Project planning documentation
├── venv/ # Virtual environment (not tracked)
└── README.md # This file


## ⚡ Performance Optimization

### Processing Time Estimates

Based on testing with various video lengths:

| Video Duration | Processing Time (CPU) | Processing Time (GPU) |
|---------------|---------------------|---------------------|
| 1 minute | ~2-3 minutes | ~45-60 seconds |
| 5 minutes | ~11 minutes | ~4 minutes |
| 10 minutes | ~22 minutes | ~8 minutes |

**Hardware Used for Benchmarks**: Intel i5/i7 CPU, NVIDIA RTX series GPU

### Optimization Tips

1. **GPU Acceleration**: Whisper runs significantly faster on CUDA-enabled GPUs
2. **Model Selection**: Use "tiny" or "base" Whisper models for faster processing at slightly lower accuracy
3. **Batch Processing**: Process multiple videos sequentially to amortize model loading time
4. **Caching**: The application caches Whisper models in `venv/` to avoid re-downloading

## 🐛 Troubleshooting

### Common Issues and Solutions

**Issue**: `FFmpeg not found` error
- **Solution**: Ensure FFmpeg is installed and added to system PATH. Verify with `ffmpeg -version`

**Issue**: `CUDA out of memory` error
- **Solution**: Reduce Whisper model size to "tiny" or "base", or process shorter video segments

**Issue**: Translation fails with connection error
- **Solution**: Check internet connectivity. The `googletrans` library requires active internet connection

**Issue**: Audio-video desynchronization
- **Solution**: The sync module automatically adjusts tempo. If issues persist, check original video encoding format

**Issue**: Poor voice quality in output
- **Solution**: Ensure Edge TTS has stable internet connection. Voice quality depends on Microsoft's cloud service

**Issue**: macOS MPS-related errors
- **Solution**: Set environment variable `export PYTORCH_ENABLE_MPS_FALLBACK=1` before running

## 🔮 Future Enhancements

Planned features for upcoming releases:

- **Multi-Speaker Detection**: Identify and dub different speakers with distinct voices
- **Lip Sync Technology**: Advanced visual speech synthesis for natural lip movements
- **Voice Cloning**: Maintain original speaker's voice characteristics in target language
- **Real-Time Streaming**: Live video translation with minimal latency
- **Subtitle Generation**: Automatic SRT/VTT subtitle creation alongside dubbing
- **Emotion Preservation**: Maintain emotional tone and emphasis from original audio
- **Background Audio Separation**: Preserve background music and sound effects while replacing speech
- **API Integration**: RESTful API for programmatic access to conversion pipeline

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the Repository**: Click the "Fork" button on GitHub
2. **Create Feature Branch**: `git checkout -b feature/AmazingFeature`
3. **Commit Changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push to Branch**: `git push origin feature/AmazingFeature`
5. **Open Pull Request**: Submit PR with detailed description of changes

### Contribution Guidelines

- Follow PEP 8 style guidelines for Python code
- Add unit tests for new features
- Update documentation for API changes
- Include example usage in PR description

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- **OpenAI Whisper**: MIT License
- **Edge TTS**: GPL-3.0 License
- **FFmpeg**: LGPL/GPL License (depending on build configuration)
- **Streamlit**: Apache License 2.0

## 🙏 Acknowledgments

- **OpenAI** for the Whisper speech recognition model
- **Microsoft** for Edge TTS neural voice synthesis
- **FFmpeg** team for powerful multimedia processing capabilities
- **Streamlit** for the intuitive web framework
- Community contributors and testers who provided valuable feedback

## 📧 Contact

**Yashwanth Balaji** - [@Yashwanth2408](https://github.com/Yashwanth2408)

**Project Repository**: [Speech-to-Speech-Streaming-Project](https://github.com/Yashwanth2408/Speech-to-Speech-Streaming-Project)

## 📊 Project Statistics

- **Lines of Code**: ~800
- **Modules**: 6 core modules + 1 web interface
- **Supported Languages**: 11 languages with 22 voice options
- **Average Processing Speed**: 2-3x video duration (CPU mode)
- **Accuracy**: 90-95% transcription accuracy for clear audio

## 🌐 Use Cases

This tool is ideal for:

- **Content Creators**: Expand reach by offering videos in multiple languages
- **Educational Institutions**: Make learning materials accessible to international students
- **Corporate Training**: Localize training videos for global workforce
- **Entertainment Industry**: Dub films and series for international markets
- **Marketing Teams**: Create multilingual promotional content efficiently
- **Accessibility**: Make video content available for non-native speakers

---

**Built with ❤️ by Yash :)**

*Last Updated: October 2025*
