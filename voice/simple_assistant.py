from typing import Optional
import requests

try:
    from voice.stt import listen
    from voice.tts import speak
except Exception:
    import os
    import sys

    pkg_dir = os.path.dirname(__file__)
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)
    from stt import listen
    from tts import speak


# 🔥 CLOUD SEND FUNCTION
def send_to_cloud(cmd):
    try:
        url = "https://agnes-project.onrender.com/command"
        res = requests.post(url, json={"command": cmd})
        print("🌐 Sent:", cmd)
    except Exception as e:
        print("❌ Error:", e)


def handle_text(text: str) -> Optional[bool]:
    import re

    low = text.lower()
    words = re.findall(r"\w+", low)
    word_set = set(words)

    greetings = {"hello", "hi", "hey", "namaste", "namaskar", "नमस्ते", "हैलो"}

    if word_set & {"exit", "quit", "stop"}:
        speak("Goodbye.")
        return False

    if word_set & greetings:
        reply = "Hello, how can I help you?"
        print("[assistant] Reply:", reply)
        speak(reply)
        return True

    # 🔥 intents (same as before)
    try:
        from voice.intents import match_intent
    except Exception:
        from intents import match_intent

    resp = match_intent(text)
    if resp:
        print("[assistant] Reply:", resp)
        speak(resp)
        return True

    # 🔥 command parser
    try:
        from voice.command_parser import parse_command
    except Exception:
        from command_parser import parse_command

    parsed = parse_command(text)

    # 🔥 ALL FIX
    if parsed.get("device") == "all":
        parsed["device"] = "all_devices"

    if parsed.get('device') and parsed.get('action'):

        device = parsed["device"]
        action = parsed["action"]

        print(f"[assistant] Parsed: {device} {action}")

        # 🔥 mapping (ONLY FIX PART)
        mapping = {
            ("room1_light", "on"): "L1ON",
            ("room1_light", "off"): "L1OFF",
            ("room1_fan", "on"): "M1ON",
            ("room1_fan", "off"): "M1OFF",

            ("room2_light", "on"): "L2ON",
            ("room2_light", "off"): "L2OFF",

            ("room3_fan", "on"): "M2ON",
            ("room3_fan", "off"): "M2OFF",

            ("all_devices", "on"): "ALLON",
            ("all_devices", "off"): "ALLOFF",

            ("night_mode", "on"): "NIGHTON",
            ("night_mode", "off"): "NIGHTOFF",
        }

        cmd = mapping.get((device, action))

        if cmd:
            send_to_cloud(cmd)
            speak("Done")
        else:
            print("❌ Conversion failed")
            speak("Command not supported")

        return True

    # 🔥 knowledge (same as before)
    try:
        from voice.knowledge import get_summary
    except Exception:
        try:
            from knowledge import get_summary
        except Exception:
            get_summary = None

    knowledge_words = ['who is', 'what is', 'kaun', 'kya', 'tell me about']

    if get_summary and any(w in text.lower() for w in knowledge_words):
        try:
            summary = get_summary(text, sentences=2)
            if summary:
                print('[assistant] Reply:', summary)
                speak(summary)
                return True
        except:
            speak("Error fetching info")
            return True

    # 🔥 fallback
    reply = f"I heard: {text}"
    print("[assistant] Reply:", reply)
    speak(reply)
    return True


def main() -> None:
    speak("Agnes is online, how can I help you?")
    timeout_count = 0

    while True:
        text = listen()

        if text == "__TIMEOUT__":
            timeout_count += 1
            if timeout_count >= 3:
                speak("No input. Goodbye.")
                break
            continue

        if text is None:
            continue

        timeout_count = 0
        print("[assistant] Recognized:", text)

        cont = handle_text(text)
        if cont is False:
            break


if __name__ == "__main__":
    main()