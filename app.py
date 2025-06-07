from flask import Flask, request, jsonify
import os
import re
import requests

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


@app.route("/run-script", methods=["POST"])
def run_script():
    data = request.json
    cmd = (
        f"python clipopera_full_stack.py "
        f"--project \"{data['project']}\" "
        f"--status \"{data['status']}\" "
        f"--link \"{data['link']}\" "
        f"--budget {data['budget']} "
        f"--drive \"{data['drive']}\" "
        f"--webmaster \"{data['webmaster']}\" "
        f"--codex \"{data['codex']}\" "
        f"--gpts \"{data.get('gpts', '')}\" "
        f"{'--sora' if data.get('sora') else ''}"
    )
    os.system(cmd)
    return jsonify({"status": "Triggered full stack script."})


@app.route("/send-prompt", methods=["POST"])
def send_prompt():
    if not DISCORD_WEBHOOK_URL:
        return jsonify({"error": "DISCORD_WEBHOOK_URL not configured"}), 500
    data = request.json
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400
    prompt = re.sub(r"[^\w\s.,:;'\"!?()-]", "", prompt)
    resp = requests.post(
        DISCORD_WEBHOOK_URL, json={"content": f"/imagine prompt: {prompt}"}
    )
    if resp.status_code == 204:
        return jsonify({"status": "Prompt successfully sent"}), 200
    return (
        jsonify({"error": f"Failed to send prompt: {resp.text}"}),
        500,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
