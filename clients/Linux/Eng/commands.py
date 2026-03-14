import datetime
import subprocess
import webbrowser
import Levenshtein

# ==========================
# FUZZY MATCH SETTINGS
# ==========================

THRESHOLD = 0.75


def similarity(a: str, b: str):
    return Levenshtein.ratio(a.lower(), b.lower())


# ==========================
# COMMAND LIST
# ==========================

COMMANDS = {
    "open discord": "discord",
    "open chrome": "google-chrome",
    "open youtube": "youtube",
    "open chatgpt": "chatgpt",
    "little brother": "little brother",
    "bigger sister": "helping",
    "open visual studio code": "code",
    "time": "time",
    "shutdown": "shutdown",
    "restart": "restart",
    "log out": "logout",
    "kill your self": "stop"
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

def open_app(command, message):
    try:
        subprocess.Popen([command])
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
    # OPEN DISCORD
    # ======================

    if action == "discord":
        return open_app("discord", "Opening Discord")

    # ======================
    # OPEN CHROME
    # ======================

    if action == "google-chrome":
        return open_app("google-chrome", "Opening Chrome")

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
    # LITTLE BROTHER
    # ======================

    if action == "little brother":
        webbrowser.open("https://www.youtube.com/watch?v=LbOve_UZZ54")
        return "Helping with your little brother"
    
    if action == "helping":
        return "Oh god, just run away, " \
        "run away as fast as you can, don't look back, just run, " \
        "run for your life, save yourself, get out of there, don't stop, keep running, " \
        "find a safe place, call for help, do whatever it takes to stay safe, just run! Calling FBI"

    # ======================
    # OPEN VS CODE
    # ======================

    if action == "code":
        return open_app("code", "Opening Visual Studio Code")

    # ======================
    # SHUTDOWN
    # ======================

    if action == "shutdown":
        subprocess.Popen(["shutdown", "-h", "now"])
        return "Shutting down your computer."

    # ======================
    # RESTART
    # ======================

    if action == "restart":
        subprocess.Popen(["shutdown", "-r", "now"])
        return "Restarting your computer."

    # ======================
    # LOG OUT
    # ======================

    if action == "logout":
        subprocess.Popen(["gnome-session-quit", "--logout", "--no-prompt"])
        return "Logging out..."

    # ======================
    # STOP JARVIS
    # ======================

    if action == "stop":
        jarvis_wake.running = False
        return "Goodbye! Have a nice day!"

    return None