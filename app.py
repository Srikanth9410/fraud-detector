import whisper
from openai import OpenAI
import os
import pyaudio
import wave
import asyncio
import websockets
import json

# --- Audio Recording Constants ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5 # Process audio in 5-second chunks
WAVE_OUTPUT_FILENAME = "temp_audio_chunk.wav"

# --- WebSocket Server ---
connected_clients = set()

async def handler(websocket):
    """Handles WebSocket connections."""
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)

async def send_to_clients(message):
    """Sends a message to all connected WebSocket clients."""
    if connected_clients:
        await asyncio.wait([client.send(json.dumps(message)) for client in connected_clients])

def display_warning(text, reasoning):
    """Sends a scam warning and the reasoning to the frontend via WebSocket."""
    print(f"⚠️ WARNING: This might be a scam call. Detected text: '{text}'")
    print(f"Reasoning: {reasoning}")
    asyncio.run(send_to_clients({"type": "warning", "text": text, "reasoning": reasoning}))

def process_audio(file_path):
    """
    Transcribes audio using Whisper and checks for scam patterns using an LLM.
    """
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Transcribing audio...")
    result = model.transcribe(file_path)
    transcribed_text = result["text"]
    print(f"Transcribed text: {transcribed_text}")

    print("Checking for scam patterns...")
    # This is a simplified example. A real implementation would use a more robust prompt
    # and potentially a fine-tuned model.
    client = OpenAI()
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"""Analyze the following text for signs of a scam. First, identify any potential red flags in a step-by-step manner. Second, based on your analysis, conclude with "Final Answer: yes" or "Final Answer: no".

Text to analyze:
'{transcribed_text}'""",
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    llm_response = response.choices[0].text.strip()
    print(f"LLM response: {llm_response}")

    # Parse the response to find the final answer
    if "final answer: yes" in llm_response.lower():
        # Extract the reasoning (everything before the final answer)
        reasoning = llm_response.lower().split("final answer:")[0].strip()
        display_warning(transcribed_text, reasoning)

def record_audio():
    """Records a chunk of audio from the microphone."""
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

async def main():
    """Starts the WebSocket server and the audio processing loop."""
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set your OPENAI_API_KEY environment variable.")
        return

    print("Starting WebSocket server on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        print("Starting real-time scam detection...")
        while True:
            record_audio()
            process_audio(WAVE_OUTPUT_FILENAME)
            await asyncio.sleep(0.1) # Yield control to the event loop

if __name__ == "__main__":
    asyncio.run(main())