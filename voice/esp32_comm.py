import requests

ESP_IP = "http://10.184.221.90"   # ⚠️ अपना IP

def send_command(device: str, action: str) -> None:
    try:
        device = device.lower()
        action = action.lower()

        mapping = {
            "room1_light": {"on": "/L1ON", "off": "/L1OFF"},
            "room1_fan": {"on": "/M1ON", "off": "/M1OFF"},
            "room2_light": {"on": "/L2ON", "off": "/L2OFF"},
            "room3_fan": {"on": "/M2ON", "off": "/M2OFF"},
            "night_mode": {"on": "/NIGHTON", "off": "/NIGHTOFF"},
        }

        if device == "all_devices":
            url = ESP_IP + ("/ALLON" if action == "on" else "/ALLOFF")
        else:
            if device not in mapping or action not in mapping[device]:
                print("❌ Invalid:", device, action)
                return

            url = ESP_IP + mapping[device][action]

        print("🌐 Sending:", url)

        res = requests.get(url)

        print("✅ Response:", res.status_code)

    except Exception as e:
        print("❌ Error:", e)