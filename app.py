import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from ai_analyzer import analyze_health

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "change-this-secret-key")

latest_data = {
    "device_id": "waiting",
    "heart_rate": None,
    "spo2": None,
    "temperature": None,
    "finger_detected": False,
    "sos": False,
    "fall_detected": False,
    "temperature_alert": False,
    "bpm_alert": False,
    "spo2_alert": False,
    "mpu_ready": True,
    "acc_magnitude": 0,
    "gyro_magnitude": 0,
    "latitude": None,
    "longitude": None,
    "map_link": "",
    "status": "WAITING",
    "received_at": None,
}

latest_analysis = analyze_health(latest_data)
history = []


def check_api_key():
    incoming_key = request.headers.get("X-API-Key") or request.json.get("api_key")
    return incoming_key == API_KEY


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/sensor-data", methods=["POST"])
def receive_sensor_data():
    global latest_data, latest_analysis

    if not request.is_json:
        return jsonify({"ok": False, "error": "JSON body required"}), 400

    data = request.get_json(silent=True) or {}

    if not check_api_key():
        return jsonify({"ok": False, "error": "Invalid API key"}), 401

    data["received_at"] = datetime.now(timezone.utc).isoformat()
    latest_data = data
    latest_analysis = analyze_health(data)

    event = {
        "time": data["received_at"],
        "status": data.get("status", "UNKNOWN"),
        "risk_level": latest_analysis["risk_level"],
        "summary": latest_analysis["summary"],
        "map_link": data.get("map_link", ""),
    }

    if data.get("sos") or data.get("fall_detected") or latest_analysis["risk_level"] != "NORMAL":
        history.insert(0, event)
        del history[25:]

    return jsonify({
        "ok": True,
        "message": "Data received",
        "analysis": latest_analysis,
    })


@app.route("/api/latest")
def api_latest():
    return jsonify({
        "data": latest_data,
        "analysis": latest_analysis,
        "history": history,
    })


@app.route("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
