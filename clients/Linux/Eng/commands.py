import datetime
import subprocess
import webbrowser
import Levenshtein

# ==========================
# CONFIG – EDIT PATHS HERE
# ==========================

STEAM_PATH = r"D:\Steam\Steam.exe"
VSCODE_PATH = r"D:\VSCode\Code.exe"
DISCORD_PATH = r"D:\Discord\Update.exe --processStart Discord.exe"

# ==========================
# FUZZY MATCH
# ==========================

def fuzzy_match(a: str, b: str, threshold=0.6):
    return Levenshtein.ratio(a.lower(), b.lower()) >= threshold

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
    # OPEN CHROME
    # ========================
    if fuzzy_match(text, "open chrome"):
        try:
            subprocess.Popen("chrome.exe")
            return "Opening Chrome"
        except:
            return "Chrome not found."

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
    # OPEN STEAM (D:)
    # ========================
    if fuzzy_match(text, "open steam"):
        try:
            subprocess.Popen(STEAM_PATH)
            return "Opening Steam"
        except Exception as e:
            return f"Steam error: {e}"

    # ========================
    # OPEN VS CODE (D:)
    # ========================
    if fuzzy_match(text, "open vs code") or fuzzy_match(text, "open visual studio"):
        try:
            subprocess.Popen(VSCODE_PATH)
            return "Opening Visual Studio Code"
        except Exception as e:
            return f"VS Code error: {e}"

    # ========================
    # OPEN DISCORD (D:)
    # ========================
    if fuzzy_match(text, "open discord"):
        try:
            subprocess.Popen(DISCORD_PATH, shell=True)
            return "Opening Discord"
        except Exception as e:
            return f"Discord error: {e}"

    return None