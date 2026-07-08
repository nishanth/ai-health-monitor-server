import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from ai_analyzer import analyze_health

# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# ============================================================
# API KEY
# ============================================================

API_KEY = os.environ.get("API_KEY", "change-this-secret-key")

# ============================================================
# PROJECT INFORMATION
# ============================================================

PROJECT_INFO = {

    "title": "AI Based Smart Health Monitoring System",

    "subtitle": "AI Powered Elderly & Patient Healthcare Monitoring",

    "student_name": "Danny Joel",

    "class": "Grade VII",

    "school": "Nanjil Catholic School CBSE",

    "place": "Vazhuthalampallam",

    "district": "Kanyakumari District",

    "country": "India",

    "developer": "Danny Joel"

}

# ============================================================
# PATIENT INFORMATION
# ============================================================

PATIENT_INFO = {

    "patient_id": "P001",

    "patient_name": "Demo Patient",

    "age": 72,

    "gender": "Male",

    "blood_group": "B+",

    "category": "Elderly Person"

}

# ============================================================
# SYSTEM STATUS
# ============================================================

SYSTEM_STATUS = {

    "device": "Offline",

    "wifi": "Disconnected",

    "cloud": "Connected",

    "render": "Running",

    "gps": "Waiting",

    "ai": "Ready"

}

# ============================================================
# LATEST SENSOR DATA
# ============================================================

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

    "received_at": None

}

# ============================================================
# AI INITIALIZATION
# ============================================================

latest_analysis = analyze_health(latest_data)

history = []

# ============================================================
# API KEY VALIDATION
# ============================================================

def check_api_key():

    if not request.is_json:
        return False

    incoming_key = (
        request.headers.get("X-API-Key")
        or request.json.get("api_key")
    )

    return incoming_key == API_KEY

# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def dashboard():

    return render_template("dashboard.html")

# ============================================================
# RECEIVE SENSOR DATA
# ============================================================

@app.route("/api/sensor-data", methods=["POST"])
def receive_sensor_data():

    global latest_data
    global latest_analysis

    if not request.is_json:

        return jsonify({

            "ok": False,

            "error": "JSON body required"

        }),400

    data = request.get_json(silent=True) or {}

    if not check_api_key():

        return jsonify({

            "ok": False,

            "error":"Invalid API Key"

        }),401

    # --------------------------------------------------------

    data["received_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    latest_data = data

    # --------------------------------------------------------

    latest_analysis = analyze_health(data)

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    SYSTEM_STATUS["device"] = "Online"

    SYSTEM_STATUS["wifi"] = "Connected"

    SYSTEM_STATUS["cloud"] = "Connected"

    SYSTEM_STATUS["render"] = "Running"

    SYSTEM_STATUS["gps"] = (
        "Connected"
        if data.get("latitude") is not None
        else "Waiting"
    )

    # --------------------------------------------------------
    # AI MEDICAL REPORT
    # --------------------------------------------------------

    latest_analysis["medical_report"] = {

        "doctor":"AI Health Assistant",

        "generated_time":data["received_at"],

        "health_score":
        max(0,100-latest_analysis["risk_score"]*10),

        "overall_condition":
        latest_analysis["risk_level"],

        "prediction":

        "Patient condition is expected to remain stable."

        if latest_analysis["risk_level"]=="NORMAL"

        else

        "Patient requires continuous monitoring.",

        "next_check":"5 Minutes",

        "hospital_required":

        latest_analysis["risk_level"]

        in

        ["HIGH","CRITICAL"]

    }

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    event = {

        "time":data["received_at"],

        "status":data.get("status","UNKNOWN"),

        "risk_level":
        latest_analysis["risk_level"],

        "health_score":
        latest_analysis["medical_report"]["health_score"],

        "summary":
        latest_analysis["summary"],

        "recommendation":

        latest_analysis["recommendations"][0]

        if latest_analysis["recommendations"]

        else "",

        "map_link":

        data.get("map_link","")

    }

    if (

        data.get("sos")

        or

        data.get("fall_detected")

        or

        latest_analysis["risk_level"]!="NORMAL"

    ):

        history.insert(0,event)

        del history[25:]

    return jsonify({

        "ok":True,

        "message":"Sensor Data Received",

        "analysis":latest_analysis

    })
    # ============================================================
# LATEST DATA API
# ============================================================

@app.route("/api/latest")
def api_latest():

    return jsonify({

        "project": PROJECT_INFO,

        "patient": PATIENT_INFO,

        "system": SYSTEM_STATUS,

        "data": latest_data,

        "analysis": latest_analysis,

        "history": history,

        "server_time":
            datetime.now(timezone.utc).isoformat()

    })


# ============================================================
# PROJECT INFORMATION API
# ============================================================

@app.route("/api/project")
def api_project():

    return jsonify({

        "project": PROJECT_INFO

    })


# ============================================================
# PATIENT INFORMATION API
# ============================================================

@app.route("/api/patient")
def api_patient():

    return jsonify({

        "patient": PATIENT_INFO

    })


# ============================================================
# SYSTEM STATUS API
# ============================================================

@app.route("/api/system")
def api_system():

    return jsonify({

        "system": SYSTEM_STATUS

    })


# ============================================================
# AI MEDICAL REPORT API
# ============================================================

@app.route("/api/report")
def api_report():

    return jsonify({

        "medical_report":

            latest_analysis.get(
                "medical_report",
                {}
            ),

        "risk_level":

            latest_analysis.get(
                "risk_level"
            ),

        "risk_score":

            latest_analysis.get(
                "risk_score"
            ),

        "recommendations":

            latest_analysis.get(
                "recommendations",
                []
            ),

        "priority_actions":

            latest_analysis.get(
                "priority_actions",
                []
            ),

        "summary":

            latest_analysis.get(
                "summary"
            )

    })


# ============================================================
# HISTORY API
# ============================================================

@app.route("/api/history")
def api_history():

    return jsonify({

        "count": len(history),

        "history": history

    })


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

@app.route("/api/statistics")
def statistics():

    total_events = len(history)

    emergency_count = 0

    warning_count = 0

    normal_count = 0

    for item in history:

        level = item["risk_level"]

        if level == "CRITICAL":

            emergency_count += 1

        elif level in ["HIGH", "MEDIUM"]:

            warning_count += 1

        else:

            normal_count += 1

    return jsonify({

        "total_events": total_events,

        "emergency_events": emergency_count,

        "warning_events": warning_count,

        "normal_events": normal_count,

        "device_status":
            SYSTEM_STATUS["device"],

        "cloud_status":
            SYSTEM_STATUS["cloud"],

        "render_status":
            SYSTEM_STATUS["render"]

    })


# ============================================================
# ABOUT API
# ============================================================

@app.route("/about")
def about():

    return jsonify({

        "project":

            PROJECT_INFO["title"],

        "student":

            PROJECT_INFO["student_name"],

        "class":

            PROJECT_INFO["class"],

        "school":

            PROJECT_INFO["school"],

        "district":

            PROJECT_INFO["district"],

        "developer":

            PROJECT_INFO["developer"],

        "version":

            "2.0"

    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "Running",

        "server": "Render",

        "project":

            PROJECT_INFO["title"],

        "student":

            PROJECT_INFO["student_name"],

        "device":

            SYSTEM_STATUS["device"],

        "cloud":

            SYSTEM_STATUS["cloud"],

        "ai":

            SYSTEM_STATUS["ai"],

        "time":

            datetime.now(
                timezone.utc
            ).isoformat()

    })


# ============================================================
# 404 PAGE
# ============================================================

@app.errorhandler(404)
def page_not_found(e):

    return jsonify({

        "ok": False,

        "message": "API Not Found"

    }),404


# ============================================================
# 500 PAGE
# ============================================================

@app.errorhandler(500)
def server_error(e):

    return jsonify({

        "ok": False,

        "message": "Internal Server Error"

    }),500


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    print("==============================================")
    print(" AI BASED SMART HEALTH MONITORING SYSTEM")
    print("==============================================")
    print(" Student :", PROJECT_INFO["student_name"])
    print(" School  :", PROJECT_INFO["school"])
    print(" Project :", PROJECT_INFO["title"])
    print("==============================================")

    app.run(

        host="0.0.0.0",

        port=port,

        debug=True

    )
