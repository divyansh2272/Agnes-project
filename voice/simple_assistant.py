"""Simple voice assistant (Step 2).

Features:
- Listens from microphone (uses `speech_recognition` via `stt.listen`).
- Speaks responses with `pyttsx3` via `tts.speak`.
- Replies "Hello, how can I help you?" when user says "hello".
- Handles unrecognized speech with a polite message.

Keep this file simple and beginner-friendly.
"""
from typing import Optional

try:
    from voice.stt import listen
    from voice.tts import speak
except Exception: 
    # Support running directly: `python voice/simple_assistant.py`
    import os
    import sys

    pkg_dir = os.path.dirname(__file__)
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)
    from stt import listen
    from tts import speak


def handle_text(text: str) -> Optional[bool]:
    """Simple intent handling with robust greeting detection.

    Returns True to continue loop, False to stop.
    """
    import re

    low = text.lower()
    # Tokenize to check whole words (avoids matching inside other words)
    words = re.findall(r"\w+", low)
    word_set = set(words)

    # Greetings (English + simple Hindi forms)
    greetings = {"hello", "hi", "hey", "namaste", "namaskar", "नमस्ते", "हैलो"}
    if word_set & {"exit", "quit", "stop"}:
        speak("Goodbye.")
        return False

    if word_set & greetings:
        # Reply both in text (console) and voice
        reply = "Hello, how can I help you?"
        print("[assistant] Reply:", reply)
        speak(reply)
        return True

    # Check small-intent responses first
    try:
        from voice.intents import match_intent
    except Exception:
        # support direct script run
        from intents import match_intent

    resp = match_intent(text)
    if resp:
        print("[assistant] Reply:", resp)
        speak(resp)
        return True

    # Try to parse as a device command (smart home)
    try:
        from voice.command_parser import parse_command
        from voice.smart_home import apply_command, get_last_device
    except Exception:
        from command_parser import parse_command
        from smart_home import apply_command, get_last_device

    parsed = parse_command(text)

    # Resolve pronouns referring to last device (Hindi: 'isse','isko','use'; English: 'this','it')
    pronouns = ['isse', 'isko', 'use', 'usko', 'us', 'issey', 'isko', 'is', 'this', 'it']
    if not parsed.get('device'):
        if any(p in text.lower() for p in pronouns):
            last = get_last_device()
            if last:
                # patch parsed to point to last device
                parsed['device'] = last
                # infer device_type and location from device name
                if last.startswith('all_'):
                    parsed['device_type'] = last.replace('all_', '').rstrip('s')
                    parsed['location'] = 'all'
                else:
                    parts = last.split('_')
                    if len(parts) == 2:
                        parsed['location'], parsed['device_type'] = parts[0], parts[1]

    if parsed.get('device') and parsed.get('action'):
        result = apply_command(parsed)
        msg = result.get('message', 'Done')
        print('[assistant] Reply:', msg)
        speak(msg)
        return True

    # Knowledge queries: try Wikipedia for short factual answers
    try:
        from voice.knowledge import get_summary
    except Exception:
        try:
            from knowledge import get_summary
        except Exception:
            get_summary = None

    # detect likely knowledge questions (English or Hindi keywords)
    knowledge_words = ['who is', 'who was', 'what is', 'what are', 'kaun', 'kon', 'kya', 'bataye', 'batayein', 'tell me about']
    if get_summary is not None and any(w in text.lower() for w in knowledge_words):
        try:
            summary = get_summary(text, sentences=2)
            if summary:
                print('[assistant] Reply (knowledge):', summary)
                speak(summary)
                return True
            else:
                speak('Sorry, I could not find information on that topic.')
                return True
        except Exception as e:
            print('[assistant] Knowledge error:', e)
            speak('Sorry, I could not fetch information right now.')
            return True

    # Default: echo back what was heard (both text and voice)
    reply = f"I heard: {text}"
    print("[assistant] Reply:", reply)
    speak(reply)
    return True


def main() -> None:
    """Run the assistant loop."""
    speak("....... .......Agnes is online, how can I help you?.")
    timeout_count = 0
    MAX_TIMEOUTS = 3
    while True:
        # Listen (supports Hindi+English with 'en-IN' default)
        text = listen()
        # If listen returned the special timeout token, count and maybe exit
        if text == "__TIMEOUT__":
            timeout_count += 1
            if timeout_count >= MAX_TIMEOUTS:
                speak("No input detected for a while. Exiting. Goodbye.")
                break
            continue
        # Other errors: unknown speech (None)
        if text is None:
            continue
        # successful recognition -> reset timeout counter
        timeout_count = 0
        print("[assistant] Recognized:", text)

        cont = handle_text(text)
        if cont is False:
            break


if __name__ == "__main__":
    main()
