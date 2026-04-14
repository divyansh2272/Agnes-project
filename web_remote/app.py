from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 🔥 command memory
last_command = "NONE"


@app.route("/")
def home():
    return render_template("index.html")


# 🔥 command receive (voice/web)
@app.route("/command", methods=["POST"])
def command():
    global last_command

    data = request.json
    cmd = data.get("command")

    print("Received:", cmd)

    last_command = cmd   # 🔥 store only

    return jsonify({
        "status": "ok",
        "msg": f"Command stored: {cmd}"
    })


# 🔥 ESP32 fetch करेगा यहाँ से
@app.route("/get")
def get_command():
    global last_command

    cmd = last_command
    last_command = "NONE"   # 🔥 reset

    return cmd


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)