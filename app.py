from flask import Flask, request, jsonify
import os

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
