import os
import csv
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
import requests

from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

# Azure Face credentials from environment
ENDPOINT = os.environ.get("FACE_ENDPOINT")
KEY = os.environ.get("FACE_APIKEY")
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.environ.get("PUSHOVER_API_TOKEN")

if not ENDPOINT or not KEY:
    raise RuntimeError("FACE_ENDPOINT and FACE_APIKEY must be set as environment variables.")

face_client = FaceClient(ENDPOINT, AzureKeyCredential(KEY))

app = Flask(__name__, static_folder="static", static_url_path="/")
CSV_FILE = "detections.csv"

logging.basicConfig(level=logging.INFO)

def send_pushover_message(title, message, sound=None):
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        app.logger.warning("Pushover credentials not configured.")
        return
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message,
    }
    if sound:
        data["sound"] = sound
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data=data
        )
        response.raise_for_status()
    except requests.RequestException as e:
        app.logger.error(f"Pushover request failed: {e}")

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

    user_agent = request.headers.get("User-Agent", "")
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip_address and "," in ip_address:
        ip_address = ip_address.split(",")[0].strip()

    try:
        with open(CSV_FILE, "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.utcnow().isoformat(),
                detected,
                len(faces),
                ip_address,
                user_agent
            ])
    except Exception as e:
        app.logger.error(f"Failed to write to CSV: {e}")

    message = (
        f"Face detected: {detected}\n"
        f"IP: {ip_address}\n"
        f"User-Agent: {user_agent}"
    )

    if detected:
        send_pushover_message("Face Detection", message, sound="bugle")
    else:
        send_pushover_message("Face Detection", message, sound="tugboat")

    return jsonify({"faceDetected": detected})

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    port = int(os.environ.get("WEBSITES_PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)

