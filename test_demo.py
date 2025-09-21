import whisper
from openai import OpenAI
import os
import asyncio
import websockets
import json

SAMPLE_AUDIO_FILE = "sample_audio.wav"
connected_clients = set()
last_warning = None
last_reasoning = None

async def handler(websocket):
    connected_clients.add(websocket)
    print("Client connected! Total clients:", len(connected_clients))

    # Send the latest warning immediately to new clients
    if last_warning:
        await websocket.send(json.dumps({
            "type": "warning",
            "text": last_warning,
            "reasoning": last_reasoning
        }))

    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print("Client disconnected. Total clients:", len(connected_clients))

async def send_to_clients(message):
    for client in connected_clients.copy():  # copy to avoid modification during iteration
        try:
            await client.send(json.dumps(message))
        except:
            connected_clients.remove(client)

async def display_warning(text, reasoning):
    global last_warning, last_reasoning
    last_warning = text
    last_reasoning = reasoning
    print(f"⚠️ WARNING: {text}")
    print(f"Reasoning: {reasoning}")
    await send_to_clients({"type": "warning", "text": text, "reasoning": reasoning})

async def process_audio(file_path):
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Transcribing audio...")
    result = model.transcribe(file_path)
    transcribed_text = result["text"]
    print(f"Transcribed text: {transcribed_text}")

    print("Checking for scam patterns...")
    client = OpenAI()
    prompt = f"""Analyze the following text for signs of a scam. List red flags step-by-step. Conclude with "Final Answer: yes" or "Final Answer: no".

Text:
'{transcribed_text}'"""
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=400,
        temperature=0
    )
    llm_response = response.choices[0].text.strip()
    print(f"LLM response: {llm_response}")

    if "final answer: yes" in llm_response.lower():
        reasoning = llm_response.lower().split("final answer:")[0].strip()
        await display_warning(transcribed_text, reasoning)

async def main():
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set your OPENAI_API_KEY environment variable.")
        return

    server = await websockets.serve(handler, "127.0.0.1", 8765)
    print("WebSocket server running on ws://127.0.0.1:8765")

    # Pr