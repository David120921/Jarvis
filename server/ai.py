import requests

LLM_API = "https://api-inference.huggingface.co/models/google/flan-t5-small"
TTS_API_URL = "https://api.streamelements.com/kappa/v2/speech"
from .config import TTS_VOICE

def generate_reply(prompt: str) -> str:
    try:
        r = requests.post(
            LLM_API,
            json={"inputs": prompt},
            timeout=20
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return data[0].get("generated_text", "")
        return "AI could not respond."
    except Exception as e:
        print("LLM error:", e)
        return "AI connection failed."

def speak_online(text: str):
    try:
        r = requests.get(TTS_API_URL, params={"voice": TTS_VOICE, "text": text})
        if r.status_code == 200:
            import tempfile, webbrowser
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(r.content)
                f.flush()
                webbrowser.open(f"file://{f.name}")
    except Exception as e:
        print("TTS error:", e)