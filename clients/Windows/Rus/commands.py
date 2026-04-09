import datetime
import subprocess
import webbrowser
import Levenshtein

# ==========================
# CONFIG – WINDOWS PATHS
# ==========================

STEAM_PATH = r"D:\Steam\Steam.exe"
VSCODE_PATH = r"D:\VSCode\Code.exe"
DISCORD_PATH = r"D:\Discord\Update.exe --processStart Discord.exe"
CHROME_PATH = "chrome.exe"

# ==========================
# FUZZY MATCH SETTINGS
# ==========================

THRESHOLD = 0.75

def similarity(a: str, b: str):
    return Levenshtein.ratio(a.lower(), b.lower())

# ==========================
# COMMAND LIST (LIKE CODE 1)
# ==========================

COMMANDS = {
    "open chrome": "chrome",
    "open youtube": "youtube",
    "open chatgpt": "chatgpt",
    "open steam": "steam",
    "open visual studio code": "vscode",
    "open discord": "discord",
    "little brother": "blue tractor",
    "time": "time",
    "shutdown": "shutdown",
    "restart": "restart",
    "log out": "logout"
}

# ==========================
# FIND CLOSEST COMMAND
# ==========================

def closest_command(text):
    best_match = None
    best_score = 0

    for command in COMMANDS:
        score = similarity(text, command)

        if score > best_score:
            best_score = score
            best_match = command

    if best_score >= THRESHOLD:
        return best_match

    return None

# ==========================
# APP LAUNCHER
# ==========================

def open_app(command, message, shell=False):
    try:
        subprocess.Popen(command, shell=shell)
        return message
    except Exception as e:
        return f"Error opening app: {e}"

# ==========================
# MAIN COMMAND HANDLER
# ==========================

def run_command(text: str):

    text = text.lower().strip()

    command = closest_command(text)

    if command is None:
        return None

    action = COMMANDS[command]

    # ======================
    # TIME
    # ======================

    if action == "time":
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The time is {now}"
    
    # ======================
    # Little Brother
    # ======================

    if action == "blue tractor":
        webbrowser.open("https://www.youtube.com/watch?v=LbOve_UZZ54&list=RDLbOve_UZZ54&start_radio=1")
        return "Helping with your little brother "

    # ======================
    # OPEN CHROME
    # ======================

    if action == "chrome":
        return open_app(CHROME_PATH, "Opening Chrome")

    # ======================
    # OPEN YOUTUBE
    # ======================

    if action == "youtube":
        webbrowser.open("https://youtube.com")
        return "Opening YouTube"

    # ======================
    # OPEN CHATGPT
    # ======================

    if action == "chatgpt":
        webbrowser.open("https://chat.openai.com")
        return "Opening ChatGPT"

    # ======================
    # OPEN STEAM
    # ======================

    if action == "steam":
        return open_app(STEAM_PATH, "Opening Steam")

    # ======================
    # OPEN VS CODE
    # ======================

    if action == "vscode":
        return open_app(VSCODE_PATH, "Opening Visual Studio Code")

    # ======================
    # OPEN DISCORD
    # ======================

    if action == "discord":
        return open_app(DISCORD_PATH, "Opening Discord", shell=True)

    # ======================
    # SHUTDOWN (WINDOWS)
    # ======================

    if action == "shutdown":
        subprocess.Popen("shutdown /s /t 1", shell=True)
        return "Shutting down your computer."

    # ======================
    # RESTART (WINDOWS)
    # ======================

    if action == "restart":
        subprocess.Popen("shutdown /r /t 1", shell=True)
        return "Restarting your computer."

    # ======================
    # LOG OUT (WINDOWS)
    # ======================

    if action == "logout":
        subprocess.Popen("shutdown /l", shell=True)
        return "Logging out..."

    return None