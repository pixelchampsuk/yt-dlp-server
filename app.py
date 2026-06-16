import subprocess, tempfile, os, glob, logging
from flask import Flask, request, send_file, jsonify

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

@app.route("/", methods=["POST"])
def extract():
    data = request.get_json()
    url = data.get("url")
    app.logger.info(f"Received request for URL: {url}")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        out_template = os.path.join(tmpdir, "audio.%(ext)s")
        
        app.logger.info("Starting yt-dlp...")
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

        app.logger.info(f"yt-dlp stdout: {result.stdout}")
        app.logger.error(f"yt-dlp stderr: {result.stderr}")

        if result.returncode != 0:
            app.logger.error(f"yt-dlp failed with code {result.returncode}")
            return jsonify({"error": result.stderr}), 500

        files = glob.glob(os.path.join(tmpdir, "*"))
        app.logger.info(f"Files produced: {files}")

        if not files:
            return jsonify({"error": "No output file produced"}), 500

        return send_file(
            files[0],
            mimetype="audio/mpeg",
            as_attachment=False
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
