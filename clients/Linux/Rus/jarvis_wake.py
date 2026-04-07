import queue
import sounddevice as sd
import vosk
import json
import requests
import tempfile
import threading
import time
import os
import signal
import asyncio
import edge_tts
import pygame
import Levenshtein
import commands 
from colorama import Fore, Style

# ==============================
# CONFIG
# ==============================

MODEL_PATH = "vosk-model-small-ru-0.22"
SERVER_URL = "http://127.0.0.1:8000/jarvis"
DEVICE_ID = "voice_client"
WAKE_WORD = "Джарвис"

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
COMMAND_TIMEOUT = 6  # seconds

VOICE = "ru-RU-DmitryNeural"

# ==============================
# GLOBAL STATE
# ==============================

audio_queue = queue.Queue()
is_speaking = False
running = True

# ==============================
# FUZZY MATCH FUNCTION
# ==============================

def fuzzy_match(a: str, b: str, threshold=0.75):
    ratio = Levenshtein.ratio(a.lower(), b.lower())
    return ratio >= threshold

# ==============================
# Load Vosk Model
# ==============================

print(Fore.GREEN)
print("Loading Vosk model...")
model = vosk.Model(MODEL_PATH)
print("Model loaded.")
print(Style.RESET_ALL)

# ==============================
# Audio Callback
# ==============================

def audio_callback(indata, frames, time_info, status):
    global is_speaking
    if status:
        print("Audio status:", status)
    if not is_speaking:
        audio_queue.put(bytes(indata))

# ==============================
# TTS Function
# ==============================

def speak(text: str):
    global is_speaking

    def _run():
        global is_speaking
        is_speaking = True
        print(Fore.CYAN)
        print("Jarvis:", text)

        async def generate():
            try:
                communicate = edge_tts.Communicate(text, VOICE)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    temp_path = f.name

                await communicate.save(temp_path)

                pygame.mixer.init()
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                os.remove(temp_path)

            except Exception as e:
                print(Fore.RED)
                print("TTS error:", e)
                print(Style.RESET_ALL)

        try:
            asyncio.run(generate())
        finally:
            is_speaking = False

    threading.Thread(target=_run, daemon=True).start()

# ==============================
# AI Server Call
# ==============================

def ask_server(text: str):
    try:
        r = requests.post(
            SERVER_URL,
            json={"device_id": DEVICE_ID, "text": text},
            timeout=60
        )
        return r.json().get("reply", "No response.")
    except Exception as e:
        print(Fore.RED)
        print("Ошибка сервера:", e)
        return "У меня возникли проблемы с подключением к серверу."

# ==============================
# Check Local Commands
# ==============================

def check_local_command(text: str):
    try:
        return commands.run_command(text)
    except Exception as e:
        print(Fore.RED)
        print("Command error:", e)
        return None

# ==============================
# Listen For Phrase
# ==============================

def listen_for_phrase(timeout=None):
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    start_time = time.time()

    while running:
        if timeout and time.time() - start_time > timeout:
            return ""

        data = audio_queue.get()

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            return result.get("text", "").lower()

    return ""

# ==============================
# Graceful Shutdown
# ==============================

def shutdown_handler(sig, frame):
    global running
    print(Fore.RED)
    print("\nВыключение...")
    running = False

signal.signal(signal.SIGINT, shutdown_handler)

# ==============================
# MAIN LOOP
# ==============================
print(Style.RESET_ALL)
print("Jarvis online.")
print(f"Произнесите  '{WAKE_WORD}', чтобы активировать.\n")

with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=BLOCK_SIZE,
    dtype="int16",
    channels=1,
    callback=audio_callback
):

    while running:

        phrase = listen_for_phrase()

        if not phrase:
            continue

        # ==============================
        # FUZZY WAKE WORD DETECTION
        # ==============================

        words = phrase.split()
        wake_detected = False

        for word in words:
            if fuzzy_match(word, WAKE_WORD, 1):
                wake_detected = True
                break

        if wake_detected:
            print(Fore.BLUE)
            print("Кодовое слово обнаружено!")

            # Remove fuzzy wake word
            command_words = []

            for word in words:
                if not fuzzy_match(word, WAKE_WORD, 0.01):
                    command_words.append(word)

            command = " ".join(command_words).strip()

            if command == "":
                print(Fore.BLUE)
                speak("Да сэр.")
                command = listen_for_phrase(timeout=COMMAND_TIMEOUT)

                if command == "":
                    print(Fore.BLUE)
                    speak("Я ничего не заметил. Пожалуйста, попробуйте еще раз.")
                    continue
            print(Fore.YELLOW)
            print("Ты:", command)

            # ==============================
            # CHECK LOCAL COMMAND FIRST
            # ==============================

            local_reply = check_local_command(command)

            if local_reply:
                speak(local_reply)
            else:
                reply = ask_server(command)
                speak(reply)
print(Style.RESET_ALL)
print("Завершено без проблем.")