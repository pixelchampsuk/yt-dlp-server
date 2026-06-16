import subprocess, tempfile, os
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

@app.route("/", methods=["POST"])
def extract():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "audio.mp3")
        result = subprocess.run([
            "yt-dlp", "-x", "--audio-format", "mp3",
            "-o", out_path, url
        ], capture_output=True)

        if result.returncode != 0:
            return jsonify({"error": result.stderr.decode()}), 500

        return send_file(out_path, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)