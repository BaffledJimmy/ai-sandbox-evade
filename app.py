import os
import csv
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

# Azure Face credentials from environment
ENDPOINT = os.environ.get("FACE_ENDPOINT")
KEY = os.environ.get("FACE_APIKEY")

if not ENDPOINT or not KEY:
    raise RuntimeError("FACE_ENDPOINT and FACE_APIKEY must be set as environment variables.")

face_client = FaceClient(ENDPOINT, AzureKeyCredential(KEY))

app = Flask(__name__, static_folder="static", static_url_path="/")
CSV_FILE = "detections.csv"

logging.basicConfig(level=logging.INFO)

@app.route("/api/detect-face", methods=["POST"])
def detect_face():
    image = request.files.get("image")
    if not image:
        return jsonify({"error": "No image uploaded"}), 400

    if not image.mimetype.startswith("image/"):
        return jsonify({"error": "File must be an image"}), 400

    img_bytes = image.read()
    faces = face_client.detect(
        img_bytes,
        detection_model=FaceDetectionModel.DETECTION03,
        recognition_model=FaceRecognitionModel.RECOGNITION04,
        return_face_id=False,
    )

    detected = len(faces) > 0
    app.logger.info(f"Faces detected: {len(faces)}")

    ip = request.remote_addr or ""
    ua = request.headers.get("User-Agent", "")

    try:
        with open(CSV_FILE, "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.utcnow().isoformat(),
                detected,
                len(faces),
                ip,
                ua
            ])
    except Exception as e:
        app.logger.error(f"Failed to write to CSV: {e}")

    return jsonify({"faceDetected": detected})

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    port = int(os.environ.get("WEBSITES_PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)

