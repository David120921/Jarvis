import sys
import queue
import threading
import time
import json
import requests
import tempfile
import os
import signal
import asyncio

from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Signal, QObject

import sounddevice as sd
import vosk
import pygame
import edge_tts
import Levenshtein
import commands

# ==============================
# CONFIG
# ==============================
MODEL_PATH = "vosk-model-small-en-us-0.15"
SERVER_URL = "http://127.0.0.1:8000/jarvis"
DEVICE_ID = "voice_client"
WAKE_WORD = "jarvis"

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
COMMAND_TIMEOUT = 6  # seconds

VOICE = "en-US-AndrewMultilingualNeural"

# ==============================
# GLOBAL STATE
# ==============================
audio_queue = queue.Queue()
is_speaking = False
running = True

# ==============================
# SIGNALS FOR GUI
# ==============================
class GuiSignals(QObject):
    log_signal = Signal(str)

signals = GuiSignals()

# ==============================
# FUZZY MATCH FUNCTION
# ==============================
def fuzzy_match(a: str, b: str, threshold=0.75):
    return Levenshtein.ratio(a.lower(), b.lower()) >= threshold

# ==============================
# Load Vosk Model
# ==============================
signals.log_signal.emit("Loading Vosk model...")
model = vosk.Model(MODEL_PATH)
signals.log_signal.emit("Model loaded.\n")

# ==============================
# AUDIO CALLBACK
# ==============================
def audio_callback(indata, frames, time_info, status):
    global is_speaking
    if status:
        signals.log_signal.emit(f"Audio status: {status}")
    if not is_speaking:
        audio_queue.put(bytes(indata))

# ==============================
# TTS FUNCTION
# ==============================
def speak(text: str):
    global is_speaking

    def _run():
        global is_speaking
        is_speaking = True
        signals.log_signal.emit(f"Jarvis: {text}")

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
                signals.log_signal.emit(f"TTS error: {e}")

        try:
            asyncio.run(generate())
        finally:
            is_speaking = False

    threading.Thread(target=_run, daemon=True).start()

# ==============================
# SERVER CALL
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
        signals.log_signal.emit(f"Server error: {e}")
        return "I am having trouble connecting to the server."

# ==============================
# LOCAL COMMANDS
# ==============================
def check_local_command(text: str):
    try:
        return commands.run_command(text)
    except Exception as e:
        signals.log_signal.emit(f"Command error: {e}")
        return None

# ==============================
# LISTEN FOR PHRASE
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
# LISTENING THREAD
# ==============================
def assistant_loop():
    global running
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

            # Wake word detection
            words = phrase.split()
            wake_detected = any(fuzzy_match(word, WAKE_WORD, 1) for word in words)

            if wake_detected:
                signals.log_signal.emit("Wake word detected!")
                command_words = [w for w in words if not fuzzy_match(w, WAKE_WORD, 0.01)]
                command = " ".join(command_words).strip()

                if command == "":
                    speak("Yes sir.")
                    command = listen_for_phrase(timeout=COMMAND_TIMEOUT)
                    if command == "":
                        speak("I didn't catch anything. Please try again.")
                        continue

                signals.log_signal.emit(f"You: {command}")

                # Check local commands
                local_reply = check_local_command(command)
                if local_reply:
                    speak(local_reply)
                else:
                    reply = ask_server(command)
                    speak(reply)

# ==============================
# GUI APPLICATION
# ==============================
class JarvisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis GUI Assistant")
        self.resize(600, 400)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        self.stop_button = QPushButton("Stop Jarvis")
        self.stop_button.clicked.connect(self.stop_jarvis)

        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect signals
        signals.log_signal.connect(self.append_log)

        # Start assistant thread
        threading.Thread(target=assistant_loop, daemon=True).start()

    def append_log(self, text):
        self.text_area.append(text)

    def stop_jarvis(self):
        global running
        running = False
        self.append_log("Shutting down...")

# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    sys.exit(app.exec())