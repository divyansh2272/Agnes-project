"""Simple intent-response mapping for the assistant.

Keep responses short and beginner-friendly. This module uses keyword
matching for simplicity and supports English + a few Hindi phrases.
"""
from typing import Optional
import datetime
import random


INTENTS = [
    {"keywords": ["hello", "hi", "hey", "namaste", "namaskar", "नमस्ते", "हैलो"], "response": "Hello, how can I help you?"},
    {"keywords": ["how are you", "how r you", "how r u", "how are u", "kaise ho", "कैसे हो"], "response": "I'm fine, thank you. How are you?"},
    {"keywords": ["i am fine", "im fine", "i'm fine", "main theek hoon", "मैं ठीक हूँ"], "response": "Glad to hear that! What can I do for you today?"},
    {"keywords": ["bye", "goodbye", "see you", "exit", "quit", "stop", "alvida"], "response": "Goodbye! Have a nice day."},
    {"keywords": ["thank you", "thanks", "shukriya", "धन्यवाद"], "response": "You're welcome!"},
    {"keywords": ["what's your name", "your name", "tumhara naam", "तुम्हारा नाम"], "response": "I am Agnes, your voice assistant."},
    {"keywords": ["who created you", "who made you"], "response": "I was created by my developer."},
    {"keywords": ["help", "what can you do", "kya kar sakta"], "response": "I can answer simple questions and control smart devices. Try saying 'turn on the light' later."},
    {"keywords": ["tell me a joke", "joke", "hasao"], "response": None},
    {"keywords": ["time", "what time", "kya time"], "response": None},
    {"keywords": ["date", "what date", "aaj ki date"], "response": None},
]


JOKES = [
    "Why did the programmer quit his job? Because he didn't get arrays.",
    "I told my computer I needed a break, and it said 'No problem — I'll go to sleep.'",
    "Why do programmers prefer dark mode? Because light attracts bugs.",
]


def _get_time_response() -> str:
    now = datetime.datetime.now()
    return f"The time is {now.strftime('%I:%M %p')}"


def _get_date_response() -> str:
    now = datetime.datetime.now()
    return f"Today's date is {now.strftime('%B %d, %Y')}"


def _get_joke() -> str:
    return random.choice(JOKES)


def match_intent(text: str) -> Optional[str]:
    """Return a response string if any intent matches, otherwise None.

    Uses substring matching and handles dynamic responses for time/date/joke.
    """
    lower = text.lower()
    for intent in INTENTS:
        for kw in intent["keywords"]:
            if kw in lower:
                # dynamic responses
                if kw in ("time", "what time", "kya time"):
                    return _get_time_response()
                if kw in ("date", "what date", "aaj ki date"):
                    return _get_date_response()
                if kw in ("tell me a joke", "joke", "hasao"):
                    return _get_joke()
                # static response
                return intent["response"]
    return None
