import re
from typing import Dict, Optional

# 🔥 FIXED LOCATION MAP
LOCATION_MAP = {
    "room1": "room1", "room 1": "room1", "room one": "room1", "bedroom": "room1",
    "room2": "room2", "room 2": "room2", "room two": "room2", "kitchen": "room2",
    "room3": "room3", "room 3": "room3", "room three": "room3", "hall": "room3",
}

DEVICE_MAP = {
    "light": "light", "bulb": "light",
    "fan": "fan",
    "night": "night_mode", "night bulb": "night_mode",
}

ON_WORDS = [
    "on", "onn", "start", "chalu", "chalu karo", "on karo", "jalao",
]

OFF_WORDS = [
    "off", "stop", "band", "bandh", "band karo", "shutdown",
]


def _find_against_map(text: str, mapping: Dict[str, str]) -> Optional[str]:
    aliases = sorted(mapping.keys(), key=lambda s: -len(s))
    for alias in aliases:
        if re.search(r"\b" + re.escape(alias) + r"\b", text):
            return mapping[alias]
    return None


def _find_action(text: str) -> Optional[str]:
    for w in ON_WORDS:
        if w in text:
            return "on"
    for w in OFF_WORDS:
        if w in text:
            return "off"
    return None


def parse_command(text: str) -> Dict[str, Optional[str]]:

    if not text:
        return {"location": None, "device": None, "action": None}

    txt = text.lower()

    # 🔥 NIGHT MODE (direct fix)
    if "night" in txt:
        action = _find_action(txt) or "on"
        return {"location": "all", "device": "night_mode", "action": action}

    # 🔥 ALL DEVICES
    if "all" in txt or "sab" in txt:
        action = _find_action(txt) or "on"
        return {"location": "all", "device": "all_devices", "action": action}

    # 🔥 NORMAL FLOW
    location = _find_against_map(txt, LOCATION_MAP)
    device = _find_against_map(txt, DEVICE_MAP)
    action = _find_action(txt)

    if not (location and device and action):
        print("Unknown command")
        return {"location": location, "device": None, "action": action}

    # 🔥 FINAL DEVICE NAME
    device_name = f"{location}_{device}"

    return {
        "location": location,
        "device": device_name,
        "action": action
    }


if __name__ == "__main__":
    tests = [
        "bedroom light on",
        "hall fan off",
        "sab band karo",
        "night mode on",
    ]

    for t in tests:
        print(t, "->", parse_command(t))