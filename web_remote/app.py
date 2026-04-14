from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

last_command = "NONE"


# 🔥 SMART CONVERSION (FINAL FIX)
def convert_command(text):
    if not text:
        return "NONE"

    text = text.lower()

    # room1 light
    if "room1" in text and "light" in text:
        if "on" in text:
            return "L1ON"
        if "off" in text or "band" in text:
            return "L1OFF"

    # room1 fan
    if "room1" in text and "fan" in text:
        if "on" in text:
            return "M1ON"
        if "off" in text or "band" in text:
            return "M1OFF"

    # room2 light
    if "room2" in text and "light" in text:
        if "on" in text:
            return "L2ON"
        if "off" in text or "band" in text:
            return "L2OFF"

    # hall fan (room3 fan)
    if ("hall" in text or "room3" in text) and "fan" in text:
        if "on" in text:
            return "M2ON"
        if "off" in text or "band" in text:
            return "M2OFF"

    # 🔥 NIGHT MODE
    if "night" in text:
        if "on" in text or "chalu" in text:
            return "NIGHTON"
        if "off" in text or "band" in text:
            return "NIGHTOFF"

    # 🔥 ALL DEVICES
    if "all" in text or "sab" in text:
        if "off" in text or "band" in text:
            return "ALLOFF"
        if "on" in text or "chalu" in text:
            return "ALLON"

    return "NONE"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/command", methods=["POST"])
def command():
    global last_command

    data = request.json
    cmd = data.get("command")

    print("Received:", cmd)

    converted = convert_command(cmd)

    print("Converted:", converted)

    last_command = converted

    return jsonify({
        "status": "ok",
        "msg": f"Command stored: {converted}"
    })


@app.route("/get")
def get_command():
    global last_command

    cmd = last_command
    last_command = "NONE"

    return cmd


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)