
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("ELEVENLABS_VOICE_ID")

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json",
    "Accept": "audio/mpeg"
}

payload = {
    "text": "Hello! Welcome to NexovAI Doctor Assistant.",
    "model_id": "eleven_multilingual_v2"
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=30
)

print("HTTP Status:", response.status_code)

if response.status_code == 200:
    with open("test_voice.mp3", "wb") as file:
        file.write(response.content)

    print("SUCCESS: Voice audio generated!")
else:
    print("TTS Error:", response.text)
