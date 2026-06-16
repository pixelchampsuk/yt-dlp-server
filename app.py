import subprocess, tempfile, os, glob, logging
from flask import Flask, request, send_file, jsonify, after_this_request

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response

app.after_request(add_cors)

@app.route("/", methods=["POST", "OPTIONS"])
def extract():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json()
    url = data.get("url")
    app.logger.info(f"Received request for URL: {url}")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        out_template = os.path.join(tmpdir, "audio.%(ext)s")
        result = subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--no-playlist",
            "--no-check-certificate",
            "-o", out_template,
            url
        ], capture_output=True, text=True)

        app.logger.info(f"stdout: {result.stdout}")
        app.logger.error(f"stderr: {result.stderr}")

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        files = glob.glob(os.path.join(tmpdir, "*"))
        if not files:
            return jsonify({"error": "No output file produced"}), 500

        return send_file(files[0], mimetype="audio/mpeg", as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
