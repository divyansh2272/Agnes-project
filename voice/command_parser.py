"""Simplified command parser for the project.

This parser enforces a small fixed vocabulary:
- Locations: room1, room2, room3 (with aliases)
- Devices: light, fan, night_bulb (with aliases)
- Actions: on, off (small set of synonyms)

parse_command(text) returns a dict with keys: location, device, action, device_name
If parsing fails or a device isn't available in a room, appropriate error values are returned.
"""
import re
from typing import Dict, Optional

# Canonical mappings requested by the user
LOCATION_MAP = {
    "room1": "room1", "room 1": "room1", "room one": "room1", "bedroom": "room1",
    "room2": "room2", "room 2": "room2", "room two": "room2", "kitchen": "room2",
    "room3": "room3", "room 3": "room 3", "Dhoom 3": "room3", "Dhoom 3": "room3", "Dhoom 3": "room3", "Dhoom 3": "room3", "room three": "room3", "hall": "room3",
}

DEVICE_MAP = {
    "light": "light", "bulb": "light",
    "fan": "fan",
    "night": "night_bulb", "zero": "night_bulb", "night bulb": "night_bulb",
}

ON_WORDS = [
    "on", "onn", "start", "start karo", "chalu", "chalu karo", "chalu karen",
    "on karo", "on kar", "jalao", "jalau", "jaloo", "jalana",
    "open", "open karo",
]
OFF_WORDS = [
    "off", "of", "of f", "offf", "stop", "stop karo",
    "band", "bandh", "bandh karo", "band karo", "band kar do", "bandho",
    "close", "close karo", "shutdown", "shut down",
]


def _find_against_map(text: str, mapping: Dict[str, str]) -> Optional[str]:
    """Return first canonical value whose alias appears in text (word-boundary match)."""
    # Check longer aliases first to avoid partial matches
    aliases = sorted(mapping.keys(), key=lambda s: -len(s))
    for alias in aliases:
        if re.search(r"\b" + re.escape(alias) + r"\b", text):
            return mapping[alias]
    return None


def _find_action(text: str) -> Optional[str]:
    for w in ON_WORDS:
        if re.search(r"\b" + re.escape(w) + r"\b", text):
            return "on"
    for w in OFF_WORDS:
        if re.search(r"\b" + re.escape(w) + r"\b", text):
            return "off"
    return None


def parse_command(text: str) -> Dict[str, Optional[str]]:
    """Parse the input and return canonical `location`, `device`, `action`, and `device_name`.

    If parsing fails, returns a dict where `device_name` is None and an error message
    may be provided under the `error` key.
    """
    if not text:
        print("Unknown command")
        return {"location": None, "device": None, "action": None, "device_name": None}

    txt = text.lower()

    # Check for night-mode commands first
    NIGHT_PATTERNS = [
        r"night mode|night mod|night mod off|night mod on|nightmode|raat mode|raat ka mode|raat ka mood|raat ka mode chalu|night chalu",
        r"night mode chalu|night mod chalu|night mode on|raat chalu|raat ko chalu|night on",
        r"night mode off|night mod band|night mode bandh|raat bandh|raat mode off|end night mode",
    ]
    for pat in NIGHT_PATTERNS:
        if re.search(pat, txt):
            action = _find_action(txt) or ("on" if re.search(r"(chalu|on|start)", txt) else "off")
            return {"location": "all", "device": "night_mode", "device_type": "mode", "action": action}

    # Check for global house/device/power commands first (many variants)
    POWER_PATTERNS = [
        r"poora ghar|poore ghar|pure ghar|pura ghar|poora ghar ki|poore ghar ki|pure ghar ki|pura ghar ki",
        r"(bijli|power|electricity).*(band|off|shutdown|shut down|bandh)",
        r"emergency shut[ \-]?down|emergency shutdown|emergency off",
        r"power (off|on|band)",
        r"ghar ki bijli|ghar ki power",
    ]

    DEVICES_PATTERNS = [
        r"saare devices|saari devices|sabhi devices|sab devices|all devices|turn off all devices|turn on all devices",
        r"sabhi sab devices|saarey devices|saare devices|saare sab",
    ]

    # If any power pattern matches, treat as all_power
    for pat in POWER_PATTERNS:
        if re.search(pat, txt):
            action = _find_action(txt) or ("off" if re.search(r"(band|shutdown|shut down|emergency|off|bandh)", txt) else "on")
            return {"location": "all", "device": "all_power", "device_type": "power", "action": action}

    # If devices pattern matches, treat as all_devices
    for pat in DEVICES_PATTERNS:
        if re.search(pat, txt):
            action = _find_action(txt) or ("off" if re.search(r"(band|off|shutdown|shut down|bandh)", txt) else "on")
            return {"location": "all", "device": "all_devices", "device_type": "device", "action": action}

    # Find location
    location = _find_against_map(txt, LOCATION_MAP)

    # Find device
    device = _find_against_map(txt, DEVICE_MAP)

    # Find action
    action = _find_action(txt)

    # Validate
    if not (location and device and action):
        print("Unknown command")
        return {"location": location, "device": None, "device_type": device, "action": action}

    # Device availability rules
    if device == "fan" and location == "room2":
        print("Fan not available in this room")
        return {"location": location, "device": device, "action": action, "device_name": None}
    if device == "night_bulb" and location != "room3":
        print("Night bulb not available in this room")
        return {"location": location, "device": device, "action": action, "device_name": None}

    # Construct device name and return keys expected by smart_home
    device_name = f"{location}_{device}"

    return {"location": location, "device": device_name, "device_type": device, "action": action}


if __name__ == "__main__":
    samples = [
        "Turn on bedroom light",
        "kitchen bulb off",
        "room3 night on",
        "room2 fan on",
        "start the fan in hall",
    ]
    for s in samples:
        print(s, "->", parse_command(s))
