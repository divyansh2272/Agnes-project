"""Demo runner that uses `stt` and `tts` to get voice input and speak back.

Run this to test step 1 (Voice Input + Voice Output).
"""
try:
    from voice.stt import listen
    from voice.tts import speak
except Exception:
    # If script is run directly (python voice/voice_demo.py) the package import
    # may fail. Add the package dir to sys.path and import modules directly.
    import os
    import sys

    pkg_dir = os.path.dirname(__file__)
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)
    from stt import listen
    from tts import speak


def main():
    speak("Hello. Voice system initialized. Say something or say exit to quit.")
    while True:
        text = listen()  # default en-IN supports Hindi+English
        # handle explicit timeout token separately from unknown audio
        if text == "__TIMEOUT__":
            speak("Sorry, I did not catch that. Please try again.")
            continue
        if text is None:
            speak("Sorry, I did not catch that. Please try again.")
            continue
        print("[voice_demo] You said:", text)
        low = text.lower()
        if any(w in low for w in ("exit", "quit", "stop")):
            speak("Goodbye.")
            break
        # Simple echo response for now; later replace with NLP/intent handling
        speak(f"You said: {text}")


if __name__ == "__main__":
    main()
