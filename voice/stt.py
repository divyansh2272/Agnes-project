"""Simple speech-to-text helper using SpeechRecognition.

This module provides a beginner-friendly `listen` function that captures
audio from the default microphone and returns recognized text (Hindi/English).
Requires: `SpeechRecognition` and a microphone driver (pyaudio).
"""
import speech_recognition as sr


def listen(lang: str = "en-IN", timeout: int = 5, phrase_time_limit: int = 8) -> str | None:
    """Listen from the microphone and return recognized text.

    Args:
        lang: language code (default 'en-IN' supports Hindi+English variants).
        timeout: max seconds to wait for phrase to start.
        phrase_time_limit: max seconds for a single phrase.

    Returns:
        Recognized text, or None if nothing understood or on error.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("[stt] Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("[stt] No speech detected (timeout).")
            # return a special token for timeouts so callers can react differently
            return "__TIMEOUT__"

    try:
        text = recognizer.recognize_google(audio, language=lang)
        return text
    except sr.UnknownValueError:
        print("[stt] Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"[stt] Recognition request failed: {e}")
        return None
