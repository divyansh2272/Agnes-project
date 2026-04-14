"""Simple text-to-speech helper using pyttsx3.

Provides a `speak` function. Keeps engine in-module so repeated calls reuse it.
"""
import pyttsx3
import traceback
import platform

_engine = None
_use_sapi = False
_sapi = None

try:
    if platform.system() == "Windows":
        try:
            import win32com.client as _win32com
            _sapi = _win32com
            _use_sapi = True
            print("[tts] Windows SAPI (pywin32) available; will prefer SAPI for TTS")
        except Exception:
            _use_sapi = False
except Exception:
    _use_sapi = False


def _init_engine():
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
            _engine.setProperty('rate', 150)
            print("[tts] pyttsx3 engine initialized")
        except Exception as e:
            print("[tts] Failed to initialize pyttsx3:", e)
            traceback.print_exc()
            _engine = None
    return _engine


def _sapi_speak(text: str) -> None:
    global _sapi
    try:
        speaker = _sapi.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)
        print("[tts] SAPI spoke:", text)
    except Exception as e:
        print("[tts] SAPI speak failed:", e)
        traceback.print_exc()


def speak(text: str, rate: int | None = None) -> None:
    """Speak the given text aloud. On Windows, prefer SAPI if available.

    Args:
        text: string to speak.
        rate: optional speech rate (words per minute).
    """
    # If SAPI available on Windows, use it (more reliable on some systems)
    if _use_sapi and platform.system() == "Windows":
        try:
            _sapi_speak(text)
            return
        except Exception:
            print("[tts] SAPI speak failed, falling back to pyttsx3")

    engine = _init_engine()
    if engine is None:
        print("[tts] No TTS engine available. Install pyttsx3 and audio drivers.")
        return

    try:
        if rate is not None:
            engine.setProperty('rate', rate)
        print(f"[tts] Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
        print("[tts] Finished speaking")
    except Exception as e:
        print("[tts] Error during speak():", e)
        traceback.print_exc()
