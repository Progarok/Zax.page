import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory
from google.cloud import firestore
from google.oauth2 import service_account

app = Flask(__name__, static_folder=".")
app.config["JSON_SORT_KEYS"] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "eiei-500707-83bfcd3d778f.json")

DB_PROJECT_ID = "eiei-500707"
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
db = firestore.Client(project=DB_PROJECT_ID, credentials=credentials)
COLLECTION_NAME = "checkins"


def serialize_doc(doc):
    payload = doc.to_dict()
    payload["id"] = doc.id
    payload["created_at"] = payload.get("created_at")
    if isinstance(payload.get("created_at"), datetime):
        payload["created_at"] = payload["created_at"].isoformat()
    if isinstance(payload.get("checked_at"), datetime):
        payload["checked_at"] = payload["checked_at"].isoformat()
    return payload


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.post("/api/checkin")
def checkin():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip() or "ไม่ระบุชื่อ"
    required_fields = [
        "latitude",
        "longitude",
        "distance",
        "targetLatitude",
        "targetLongitude",
        "radius",
        "status",
    ]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        return jsonify({"success": False, "error": f"ข้อมูลไม่ครบ: {', '.join(missing)}"}), 400

    now = datetime.now(timezone.utc)
    document = {
        "name": name,
        "latitude": float(payload["latitude"]),
        "longitude": float(payload["longitude"]),
        "distance": float(payload["distance"]),
        "targetLatitude": float(payload["targetLatitude"]),
        "targetLongitude": float(payload["targetLongitude"]),
        "radius": float(payload["radius"]),
        "status": payload["status"],
        "checked_at": now,
        "created_at": now,
    }

    try:
        doc_ref = db.collection(COLLECTION_NAME).document()
        doc_ref.set(document)
    except Exception as exc:  # pragma: no cover - runtime safeguard
        return jsonify({"success": False, "error": f"ไม่สามารถบันทึกลง Firestore ได้: {exc}"}), 500

    return jsonify({"success": True, "message": "บันทึกการเช็คชื่อสำเร็จ", "id": doc_ref.id})


@app.get("/api/checkins")
def get_checkins():
    try:
        docs = (
            db.collection(COLLECTION_NAME)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(10)
            .stream()
        )
        items = [serialize_doc(doc) for doc in docs]
        return jsonify(items)
    except Exception as exc:  # pragma: no cover - runtime safeguard
        return jsonify({"error": f"ไม่สามารถโหลดข้อมูลจาก Firestore ได้: {exc}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
