import datetime
import subprocess
import webbrowser
import Levenshtein

# ==========================
# FUZZY MATCH
# ==========================

def fuzzy_match(a: str, b: str, threshold=0.6):
    return Levenshtein.ratio(a.lower(), b.lower()) >= threshold

# ==========================
# SAFE APP LAUNCHER
# ==========================

def open_app(command, success_message):
    try:
        subprocess.Popen(command.split())
        return success_message
    except Exception as e:
        return f"Error: {e}"

# ==========================
# MAIN COMMAND HANDLER
# ==========================

def run_command(text: str):
    text = text.lower()

    # ========================
    # TIME
    # ========================
    if "time" in text:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The time is {now}"

    # ========================
    # OPEN CHROME (Ubuntu)
    # ========================
    if fuzzy_match(text, "open Google"):
        return open_app("google-chrome", "Opening Chrome")

    # ========================
    # OPEN YOUTUBE
    # ========================
    if fuzzy_match(text, "open youtube"):
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube"

    # ========================
    # OPEN CHATGPT
    # ========================
    if fuzzy_match(text, "open chat gpt") or fuzzy_match(text, "open chatgpt"):
        webbrowser.open("https://chat.openai.com")
        return "Opening ChatGPT"

    # ========================
    # OPEN VS CODE (Ubuntu)
    # ========================
    if fuzzy_match(text, "open vs code") or fuzzy_match(text, "open visual studio"):
        return open_app("code", "Opening Visual Studio Code")

    # ========================
    # OPEN DISCORD (Ubuntu)
    # ========================
    if fuzzy_match(text, "open discord"):
        return open_app("discord", "Opening Discord")

    return None