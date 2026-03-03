from fastapi import FastAPI
from pydantic import BaseModel
import requests

# ==============================
# 🔑 PUT YOUR GROQ API KEY HERE
# ==============================
GROQ_API_KEY = "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"

API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

app = FastAPI()

class JarvisRequest(BaseModel):
    device_id: str
    text: str


def ask_ai(prompt: str):
    try:
        payload = {
            "model": "groq/compound",
            "messages": [
                {"role": "system", "content": "You are Jarvis, a cool and intelligent AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200
        }

        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=60
        )

        print("STATUS:", response.status_code)

        if response.status_code != 200:
            print("RESPONSE:", response.text)
            return "AI error."

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "AI failed."


@app.post("/jarvis")
def jarvis(req: JarvisRequest):
    print(f"[{req.device_id}] {req.text}")
    reply = ask_ai(req.text)
    print(f"[Jarvis -> {req.device_id}] {reply}")
    return {"reply": reply}