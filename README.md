# Elder Fraud/Scam Voice Detector MVP

This project is a Minimum Viable Product (MVP) for a voice detector that listens to phone call audio and alerts the user if it detects patterns commonly associated with scams.

## How it Works

1.  **Input**: The application continuously captures audio from the microphone in 5-second chunks.
2.  **Speech-to-Text**: It uses OpenAI's Whisper model to transcribe each audio chunk into text.
3.  **Scam Detection**: The transcribed text is sent to an OpenAI Language Model (LLM) to classify it as a potential scam.
4.  **Output**: If a scam is detected, a warning message is displayed on a web dashboard in real-time.

## Setup and Usage

### 1. Prerequisites

*   Python 3
*   An OpenAI API key
*   Homebrew (for macOS) to install `portaudio` and `ffmpeg`
*   Node.js and npm

### 2. Installation

1.  **Clone the repository or download the code.**

2.  **Install PortAudio and FFmpeg:**
    ```bash
    brew install portaudio ffmpeg
    ```

3.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Upgrade packaging tools and install backend dependencies:**
    ```bash
    python -m pip install --upgrade pip setuptools
    pip install -r requirements.txt
    ```

5.  **Install frontend dependencies:**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

### 3. Configuration

1.  **Set your OpenAI API Key:**
    ```bash
    export OPENAI_API_KEY='your-api-key'
    ```
    Replace `'your-api-key'` with your actual OpenAI API key.

### 4. Running the Application

You will need to run two separate processes in two separate terminals: the Python backend and the React frontend.

**Terminal 1: Start the Backend**
```bash
source venv/bin/activate
python app.py
```

**Terminal 2: Start the Frontend**
```bash
cd frontend
npm start
```

This will open the web dashboard in your browser, and you will see the scam alerts appear in real-time as they are detected.

## Testing with Sample Audio

For easier testing, you can use the provided scripts to generate a sample audio file and run the backend with that file. This is a great way to test the frontend without needing to speak into the microphone.

**1. Generate the Sample Audio**

Run the following command to create a `sample_audio.wav` file:
```bash
python fraud_detector/sample_audio.py
```

**2. Run the Test Demo Backend**

This will start the backend and process only the `sample_audio.wav` file.
```bash
python fraud_detector/test_demo.py
```

**3. Start the Frontend**

In a separate terminal, start the frontend as usual:
```bash
cd fraud_detector/frontend
npm start
```
The web dashboard will open and display the results from the sample audio.

## Future Improvements

*   **Improved scam detection**: Fine-tune a dedicated classification model for better accuracy and to provide more detailed information about the detected scam patterns.