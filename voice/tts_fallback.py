"""Windows SAPI TTS fallback test.

Usage:
    python -c "from voice.tts_fallback import sapi_speak; sapi_speak('Hello')"

If `pywin32` is not installed, this file will print instructions.
"""
import sys

try:
    import win32com.client
except Exception:
    win32com = None


def sapi_speak(text: str) -> None:
    """Speak using Windows SAPI (requires pywin32).

    Falls back to printing instructions if pywin32 is missing.
    """
    if win32com is None:
        print("[tts_fallback] pywin32 not installed. Install with: pip install pywin32")
        return

    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)
        print("[tts_fallback] SAPI spoke:", text)
    except Exception as e:
        print("[tts_fallback] SAPI speak failed:", e)
        raise


if __name__ == "__main__":
    sapi_speak("Testing SAPI voice output")
