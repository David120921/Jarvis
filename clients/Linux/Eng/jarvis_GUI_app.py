import customtkinter as ctk
import queue
import sounddevice as sd
import vosk
import json
import requests
import threading
import os
import Levenshtein
import commands
import sounddevice as sd
import asyncio
import edge_tts

# ==============================
# CONFIG
# ==============================

MODEL_PATH = "vosk-model-small-en-us-0.15"
SERVER_URL = "http://127.0.0.1:8000/jarvis"
DEVICE_ID = "voice_client"
WAKE_WORD = "jarvis"
TTS_TOKEN = "YOUR_TOKEN"

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

# ==============================
# GLOBAL STATE
# ==============================

audio_queue = queue.Queue()
is_speaking = False
running = False

# ==============================
# GUI
# ==============================

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("600x800")
app.title("Jarvis AI")

title = ctk.CTkLabel(app, text="JARVIS", font=("Orbitron", 30))
title.pack(pady=20)

output = ctk.CTkTextbox(app, width=500, height=400)
output.pack(pady=10)

entry = ctk.CTkEntry(app, width=350, placeholder_text="Enter command...")
entry.pack(pady=10)

# ==============================
# HELPER FUNCTIONS
# ==============================

def log(text):
    output.insert("end", text + "\n")
    output.see("end")


def fuzzy_match(a: str, b: str, threshold=0.75):
    ratio = Levenshtein.ratio(a.lower(), b.lower())
    return ratio >= threshold


# ==============================
# LOAD MODEL
# ==============================

log("Loading Vosk model...")
model = vosk.Model(MODEL_PATH)
log("Model loaded.")

# ==============================
# AUDIO CALLBACK
# ==============================

def audio_callback(indata, frames, time_info, status):
    global is_speaking
    if not is_speaking:
        audio_queue.put(bytes(indata))

# ==============================
# TTS
# ==============================

def speak(text: str):
    global is_speaking

    async def _speak_async(text):
        global is_speaking
        is_speaking = True
        print(Fore.CYAN)
        print("Jarvis:", text)

        try:
            communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
            await communicate.save("temp_voice.wav")

            # Play audio
            os.system("ffplay -nodisp -autoexit temp_voice.wav >nul 2>&1")
            os.remove("temp_voice.wav")

        except Exception as e:
            print(Fore.RED)
            print("TTS error:", e)
            print(Style.RESET_ALL)
        finally:
            is_speaking = False

    threading.Thread(target=lambda: asyncio.run(_speak_async(text)), daemon=True).start()


# ==============================
# SERVER
# ==============================

def ask_server(text):

    try:

        r = requests.post(
            SERVER_URL,
            json={"device_id": DEVICE_ID, "text": text},
            timeout=60
        )

        return r.json().get("reply", "No response.")

    except Exception as e:

        log("Server error: " + str(e))
        return "I cannot reach the server."


# ==============================
# LOCAL COMMAND
# ==============================

def check_local_command(text):

    try:
        return commands.run_command(text)

    except Exception as e:
        log("Command error: " + str(e))
        return None


# ==============================
# PROCESS COMMAND
# ==============================

def process_command(command):

    log("You: " + command)

    local_reply = check_local_command(command)

    if local_reply:
        speak(local_reply)
    else:
        reply = ask_server(command)
        speak(reply)


# ==============================
# TEXT INPUT BUTTON
# ==============================

def send_text():

    command = entry.get()

    if command.strip() == "":
        return

    entry.delete(0, "end")

    threading.Thread(target=process_command, args=(command,)).start()


button = ctk.CTkButton(app, text="Execute", command=send_text)
button.pack(pady=10)

# ==============================
# LISTEN LOOP
# ==============================

def listen_loop():

    global running

    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):

        log("Listening for wake word...")

        while running:

            data = audio_queue.get()

            if recognizer.AcceptWaveform(data):

                result = json.loads(recognizer.Result())
                phrase = result.get("text", "").lower()

                if phrase == "":
                    continue

                log("Heard: " + phrase)

                words = phrase.split()

                wake = False

                for word in words:
                    if fuzzy_match(word, WAKE_WORD, 0.8):
                        wake = True
                        break

                if wake:

                    command_words = []

                    for word in words:
                        if not fuzzy_match(word, WAKE_WORD, 0.01):
                            command_words.append(word)

                    command = " ".join(command_words)

                    if command == "":
                        speak("Yes sir.")
                        continue

                    process_command(command)

# ==============================
# START / STOP BUTTONS
# ==============================

def start_listening():

    global running

    if running:
        return

    running = True

    threading.Thread(target=listen_loop, daemon=True).start()

    log("Voice recognition started.")


def stop_listening():

    global running

    running = False

    log("Voice recognition stopped.")


start_btn = ctk.CTkButton(app, text="Start Listening", command=start_listening)
start_btn.pack(pady=5)

stop_btn = ctk.CTkButton(app, text="Stop Listening", command=stop_listening)
stop_btn.pack(pady=5)

# ==============================

app.mainloop()