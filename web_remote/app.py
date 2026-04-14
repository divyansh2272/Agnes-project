from flask import Flask, render_template, request, jsonify
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice.command_parser import parse_command
from voice.esp32_comm import send_command

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/command", methods=["POST"])
def command():
    data = request.json
    cmd = data.get("command")

    print("Received:", cmd)

    result = parse_command(cmd)

    if not result or not result.get("device"):
        return jsonify({"status": "error", "msg": "❌ Invalid command"})

    device = result["device"]
    action = result["action"]

    print(f"Sending: {device} {action}")

    send_command(device, action)

    return jsonify({
        "status": "ok",
        "msg": f"✅ Done: {device} {action}"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)