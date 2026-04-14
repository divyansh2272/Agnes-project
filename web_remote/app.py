from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

last_command = "NONE"


# 🔥 mapping (same as assistant)
def convert_command(text):
    text = text.lower()

    mapping = {
        "room1 light on": "L1ON",
        "room1 light off": "L1OFF",
        "room1 fan on": "M1ON",
        "room1 fan off": "M1OFF",

        "room2 light on": "L2ON",
        "room2 light off": "L2OFF",

        "hall fan on": "M2ON",
        "hall fan off": "M2OFF",

        "night on": "NIGHTON",
        "night off": "NIGHTOFF",

        "all off": "ALLOFF",
        "all on": "ALLON",
    }

    return mapping.get(text, "NONE")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/command", methods=["POST"])
def command():
    global last_command

    data = request.json
    cmd = data.get("command")

    print("Received:", cmd)

    # 🔥 convert here
    last_command = convert_command(cmd)

    print("Converted:", last_command)

    return jsonify({
        "status": "ok",
        "msg": f"Command stored: {last_command}"
    })


@app.route("/get")
def get_command():
    global last_command

    cmd = last_command
    last_command = "NONE"

    return cmd


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)