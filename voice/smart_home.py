"""Simple in-memory smart home simulator.

Keeps device states and applies parsed commands from `command_parser`.
"""
from typing import Dict, List, Optional
try:
    from voice.esp32_comm import send_command
except Exception:
    from esp32_comm import send_command

# Initial device list
_DEVICES = {
    'room1_light': 'off',
    'room2_light': 'off',
    'room3_light': 'off',
    'room1_fan': 'off',
    'room3_fan': 'off',
    'room3_night_bulb': 'off',
}

# Remember last controlled device (session memory)
_last_device: str | None = None

# Snapshot used when enabling night mode so we can restore previous states
_night_snapshot: Dict[str, str] | None = None


def list_devices() -> Dict[str, str]:
    return dict(_DEVICES)


def _apply_to_device(name: str, action: str) -> None:
    if name in _DEVICES:
        _DEVICES[name] = action


def set_last_device(name: str | None) -> None:
    global _last_device
    _last_device = name


def get_last_device() -> str | None:
    return _last_device


def _devices_by_type(device_type: str) -> List[str]:
    return [d for d in _DEVICES if d.endswith('_' + device_type)]


def apply_command(parsed: Dict[str, Optional[str]]) -> Dict[str, str]:
    """Apply parsed command and return a result dict.

    Returns dict with keys: 'status' ('ok'|'error'), 'message'.
    """
    device = parsed.get('device')
    action = parsed.get('action')
    device_type = parsed.get('device_type')
    location = parsed.get('location')

    if not device or not action:
        return {'status': 'error', 'message': "Couldn't determine device or action."}

    # Special: night mode -> turn off all devices except room1_fan and room3_light
    if device == 'night_mode':
        global _night_snapshot
        exceptions = {'room1_fan', 'room3_light'}
        if action == 'on':
            # save current state
            _night_snapshot = dict(_DEVICES)
            # turn off everything except exceptions
            for t in list(_DEVICES.keys()):
                if t in exceptions:
                    continue
                _apply_to_device(t, 'off')
                try:
                    send_command(t, 'off')
                except Exception:
                    pass
            set_last_device('night_mode')
            return {'status': 'ok', 'message': "Night mode enabled: saved state and turned off all devices except room1 fan and hall light."}
        else:
            # restore snapshot if available
            if _night_snapshot is None:
                set_last_device(None)
                return {'status': 'ok', 'message': "Night mode disabled (no previous state to restore)."}
            # restore each device to previous state and notify ESP32
            for name, prev_state in _night_snapshot.items():
                # only restore if device exists in current set
                if name in _DEVICES:
                    _apply_to_device(name, prev_state)
                    try:
                        send_command(name, prev_state)
                    except Exception:
                        pass
            _night_snapshot = None
            set_last_device(None)
            return {'status': 'ok', 'message': "Night mode disabled: previous device states restored."}

    # handle all_{device}s (e.g. all_lights) and special all_power/all_devices
    if device.startswith('all_'):
        # special: all_power -> toggle entire house power (apply to all devices)
        if device == 'all_power' or device == 'all_devices':
            for t in list(_DEVICES.keys()):
                _apply_to_device(t, action)
                # forward to ESP32 shim
                try:
                    send_command(t, action)
                except Exception:
                    pass
            set_last_device(device)
            return {'status': 'ok', 'message': f"Done: all devices {action}"}

        # e.g. all_lights -> device_type 'light'
        if device_type is None:
            # try infer
            if 'light' in device:
                device_type = 'light'
            elif 'fan' in device:
                device_type = 'fan'
        targets = _devices_by_type(device_type)
        for t in targets:
            _apply_to_device(t, action)
            try:
                send_command(t, action)
            except Exception:
                pass
        # remember last device type as grouped command
        set_last_device(f"all_{device_type}s")
        return {'status': 'ok', 'message': f"Done: all {device_type}s {action}"}

    # single device
    if device in _DEVICES:
        _apply_to_device(device, action)
        try:
            send_command(device, action)
        except Exception:
            pass
        set_last_device(device)
        readable = device.replace('_', ' ')
        return {'status': 'ok', 'message': f"Done: {readable} {action}"}

    # If location specified but device not in list, try build name
    if device_type and location and location != 'all':
        name = f"{location}_{device_type}"
        if name in _DEVICES:
            _apply_to_device(name, action)
            try:
                send_command(name, action)
            except Exception:
                pass
            set_last_device(name)
            readable = name.replace('_', ' ')
            return {'status': 'ok', 'message': f"Done: {readable} {action}"}

    return {'status': 'error', 'message': "Device not found."}
