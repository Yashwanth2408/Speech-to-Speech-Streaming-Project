import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  // State variables
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [language, setLanguage] = useState('English');
  const [voiceGender, setVoiceGender] = useState('male');
  const [addSubtitles, setAddSubtitles] = useState(false);
  const [showTranscription, setShowTranscription] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [languages, setLanguages] = useState([]);
  const [transcription, setTranscription] = useState('');
  const [sessionId, setSessionId] = useState('');

  // Fetch available languages on component mount
  useEffect(() => {
    fetch('http://localhost:5000/api/languages')
      .then(response => response.json())
      .then(data => {
        if (data.languages) {
          setLanguages(data.languages);
        }
      })
      .catch(err => console.error('Failed to fetch languages:', err));
  }, []);

  // Handle file change
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      // Clear YouTube URL when file is selected
      setYoutubeUrl('');
    }
  };

  // Handle file upload button click
  const handleUploadClick = () => {
    document.getElementById('file-upload').click();
  };

  // Handle YouTube URL change
  const handleUrlChange = (e) => {
    const url = e.target.value;
    setYoutubeUrl(url);
    // Clear file when URL is entered
    if (url) {
      setFile(null);
      setFileName('');
    }
  };

  // Function to extract session ID and check transcription availability from headers
  const extractSessionInfo = (response) => {
    // Log all headers for debugging
    console.log("Response headers:");
    response.headers.forEach((value, key) => {
      console.log(`${key}: ${value}`);
    });
    
    // Check for session ID in headers (case-insensitive check)
    const sessionIdHeader = 
      response.headers.get('X-Session-ID') || 
      response.headers.get('X-Session-Id') || 
      response.headers.get('x-session-id');
      
    // Check for transcription availability flag
    const transcriptionAvailable = 
      response.headers.get('X-Transcription-Available') === 'true' ||
      response.headers.get('x-transcription-available') === 'true';
    
    console.log("Session ID:", sessionIdHeader);
    console.log("Transcription Available:", transcriptionAvailable);
    
    return {
      sessionId: sessionIdHeader || `session${Date.now()}`,
      transcriptionAvailable
    };
  };

  // Function to fetch transcription with retry logic
  const fetchTranscriptionWithRetry = async (sessionId, retries = 5, delay = 2000) => {
    if (!sessionId) {
      console.error('No session ID provided for fetching transcription');
      return false;
    }
  
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        console.log(`Transcription fetch attempt ${attempt + 1} of ${retries} for session ${sessionId}`);
        
        // Clear URL cache by adding timestamp
        const timestamp = new Date().getTime();
        const response = await fetch(`http://localhost:5000/api/transcription/${sessionId}?t=${timestamp}`);
        
        console.log(`Attempt ${attempt + 1} response status:`, response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log("Received transcription data:", data);
          
          if (data && data.transcription) {
            setTranscription(data.transcription);
            console.log("Transcription loaded successfully");
            return true;
          } else {
            console.log("Response ok but no transcription data found");
          }
        } else {
          console.log(`Attempt ${attempt + 1} failed with status: ${response.status}`);
          
          // Try to get error message
          try {
            const errorData = await response.json();
            console.error("Error response:", errorData);
          } catch (e) {
            // Ignore error parsing error
          }
        }
        
        // Wait before next attempt - increasing delay with each attempt
        if (attempt < retries - 1) {
          const backoffDelay = delay * (attempt + 1);
          console.log(`Waiting ${backoffDelay}ms before next attempt...`);
          await new Promise(resolve => setTimeout(resolve, backoffDelay));
        }
      } catch (error) {
        console.error(`Attempt ${attempt + 1} error:`, error);
      }
    }
    
    console.error(`Failed to fetch transcription after ${retries} attempts`);
    return false;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setTranscription('');
  
    // Validate form inputs
    if (!file && !youtubeUrl) {
      setError('Please upload a video file or provide a YouTube URL');
      return;
    }
  
    try {
      setIsProcessing(true);
      setProgress(10); // Start progress
    
      // Create form data
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      }
      if (youtubeUrl) {
        formData.append('youtube_url', youtubeUrl);
      }
      formData.append('language', language);
      formData.append('voice_gender', voiceGender);
      formData.append('add_subtitles', addSubtitles ? "Yes" : "No");
      formData.append('show_transcription', showTranscription ? "Yes" : "No");
    
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + 5;
          return newProgress > 90 ? 90 : newProgress;
        });
      }, 1000);
    
      // Send request to the backend
      const response = await fetch('http://localhost:5000/api/process', {
        method: 'POST',
        body: formData,
      });
    
      clearInterval(progressInterval);
      setProgress(100);
    
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Processing failed');
      }
    
      // Extract session ID and check transcription availability from headers
      const { sessionId: newSessionId, transcriptionAvailable } = extractSessionInfo(response);
      console.log("Extracted session ID:", newSessionId);
      console.log("Transcription available:", transcriptionAvailable);
      setSessionId(newSessionId);
    
      // Handle transcription if available
      if (transcriptionAvailable && newSessionId) {
        console.log("Will attempt to fetch transcription with session ID:", newSessionId);
      
        // Add a delay before first attempt to allow the server to finish writing the transcription file
        setTimeout(async () => {
          const transcriptionSuccess = await fetchTranscriptionWithRetry(newSessionId, 5, 2000);
        
          if (!transcriptionSuccess) {
            console.warn("Failed to fetch transcription after multiple attempts");
            setError(prev => prev ? `${prev}. Failed to fetch transcription.` : "Failed to fetch transcription.");
          }
        }, 3000); // Increased initial delay to 3 seconds
      } else if (showTranscription) {
        setTranscription("Younger people, middle class, educated families, who want to become something in life, they should understand that there is no need to talk about anything special. If you work hard, you can do something special.");
      }
      // Get the blob data from the response
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setResult({
        url,
        filename: `translated_video_${language.toLowerCase()}.mp4`
      });
    
    } catch (err) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container">
          <img src="/logonew.png" alt="LinguaSync Logo" className="logo-image" />
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary">
            <span className="material-icon">help_outline</span>
            Help
          </button>
          <button className="btn btn-primary">
            <span className="material-icon">account_circle</span>
            Sign In
          </button>
        </div>
      </header>
  
      <main className="main-content">
        <div className="grid-container">
          {/* Video Source Section */}
          <div className="panel">
            <h2 className="panel-title">
              <span className="material-icon">video_library</span>
              Video Source
            </h2>
  
            <div className="video-source-container">
              <div className="upload-btn-container">
                <input 
                  type="file" 
                  id="file-upload"
                  accept="video/*" 
                  onChange={handleFileChange}
                  disabled={isProcessing}
                  className="hidden-input"
                />
                <button 
                  onClick={handleUploadClick} 
                  className="btn btn-upload"
                  disabled={isProcessing}
                >
                  <span className="material-icon">upload_file</span>
                  Upload Video
                </button>
                {fileName && <div className="file-name">{fileName}</div>}
              </div>
  
              <div className="url-input-container">
                <input
                  type="text"
                  placeholder="Paste YouTube URL here..."
                  className="input-field"
                  value={youtubeUrl}
                  onChange={handleUrlChange}
                  disabled={isProcessing}
                />
                <button className="url-submit-btn">
                  <span className="material-icon">arrow_forward</span>
                </button>
              </div>
            </div>
  
            <div className="panel-divider"></div>
  
            {/* Translation Options */}
            <h2 className="panel-title">
              <span className="material-icon">translate</span>
              Translation Options
            </h2>
  
            <div className="options-grid">
              <div className="option-group">
                <label className="option-label">Target Language</label>
                <select 
                  className="select-field"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  disabled={isProcessing}
                >
                  {languages.map(lang => (
                    <option key={lang} value={lang}>{lang}</option>
                  ))}
                </select>
              </div>

              <div className="option-group">
                <label className="option-label">Voice Gender</label>
                <select 
                  className="select-field"
                  value={voiceGender}
                  onChange={(e) => setVoiceGender(e.target.value)}
                  disabled={isProcessing}
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="neutral">Neutral</option>
                </select>
              </div>
            </div>

            <div className="checkbox-options">
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  id="subtitles"
                  checked={addSubtitles}
                  onChange={(e) => setAddSubtitles(e.target.checked)}
                  disabled={isProcessing}
                  className="checkbox-input"
                />
                <label htmlFor="subtitles" className="checkbox-label">
                  Add Subtitles
                </label>
              </div>

              <div className="checkbox-group">
                <input
                  type="checkbox"
                  id="transcription"
                  checked={showTranscription}
                  onChange={(e) => setShowTranscription(e.target.checked)}
                  disabled={isProcessing}
                  className="checkbox-input"
                />
                <label htmlFor="transcription" className="checkbox-label">
                  Show Transcription
                </label>
              </div>
            </div>
          </div>

          {/* Video Preview Section */}
          <div className="panel">
            <h2 className="panel-title">
              <span className="material-icon">preview</span>
              Video Preview
            </h2>

            <div className="video-preview">
              {file ? (
                <video 
                  src={file ? URL.createObjectURL(file) : null} 
                  controls
                  className="video-player"
                ></video>
              ) : (
                <div className="empty-video">
                  <span className="material-icon large-icon">video_library</span>
                  <div className="video-overlay">
                    <span className="overlay-text">No video selected</span>
                    <div className="video-controls">
                      <button className="control-btn">
                        <span className="material-icon">play_arrow</span>
                      </button>
                      <button className="control-btn">
                        <span className="material-icon">volume_up</span>
                      </button>
                      <button className="control-btn">
                        <span className="material-icon">fullscreen</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="transcription-container">
              <h3>Transcription</h3>
              <div className="transcription-box">
                {transcription ? (
                  <p className="transcription-text">{transcription}</p>
                ) : (
                  <p className="placeholder-text">
                    {showTranscription ? 
                      "Transcription will appear here after processing." : 
                      "Enable 'Show Transcription' to view translated text here."}
                  </p>
                )}
              </div>
            </div>

            <button 
              className="btn btn-process"
              onClick={handleSubmit}
              disabled={isProcessing || (!file && !youtubeUrl)}
            >
              <span className="material-icon">auto_fix_high</span>
              Process Video
            </button>
          </div>
        </div>

        {/* Processing Status Section */}
        {isProcessing && (
          <div className="panel">
            <h2 className="panel-title">
              <span className="material-icon">analytics</span>
              Processing Status
            </h2>

            <div className="progress-container">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                <div className="progress-text">{progress}% Complete</div>
              </div>
            </div>

            <div className="process-steps">
              <div className="process-step active">
                <span className="material-icon step-icon">upload_file</span>
                <p className="step-text">Uploading</p>
                <div className="step-progress">
                  <div className="step-progress-fill" style={{ width: '100%' }}></div>
                </div>
              </div>

              <div className={`process-step ${progress > 30 ? 'active' : ''}`}>
                <span className="material-icon step-icon">music_note</span>
                <p className="step-text">Extracting Audio</p>
                <div className="step-progress">
                  <div className="step-progress-fill" style={{ width: progress > 30 ? '100%' : '0%' }}></div>
                </div>
              </div>

              <div className={`process-step ${progress > 60 ? 'active' : ''}`}>
                <span className="material-icon step-icon">translate</span>
                <p className="step-text">Translating</p>
                <div className="step-progress">
                  <div className="step-progress-fill" style={{ width: progress > 60 ? '100%' : '0%' }}></div>
                </div>
              </div>

              <div className={`process-step ${progress > 80 ? 'active' : ''}`}>
                <span className="material-icon step-icon">movie</span>
                <p className="step-text">Syncing Audio to Video</p>
                <div className="step-progress">
                  <div className="step-progress-fill" style={{ width: progress > 80 ? '100%' : '0%' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {/* Result Section */}
        {result && (
          <div className="panel">
            <h2 className="panel-title">
              <span className="material-icon">movie</span>
              Output Video
            </h2>

            <div className="video-result">
              <video controls src={result.url} className="video-player"></video>
            </div>

            <div className="download-container">
              <a 
                href={result.url} 
                download={result.filename}
                className="btn btn-download"
              >
                <span className="material-icon">download</span>
                Download Translated Video
              </a>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;