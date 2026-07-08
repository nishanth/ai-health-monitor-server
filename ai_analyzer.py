"""
============================================================

AI BASED SMART HEALTH MONITORING SYSTEM
AI HEALTH ANALYZER v2.0

Developed for School Science Competition

============================================================
"""

# ============================================================
# CONFIGURATION
# ============================================================

NORMAL_TEMP = 36.0
WARNING_TEMP = 37.5
DANGER_TEMP = 38.5

LOW_BPM = 50
NORMAL_BPM = 80
HIGH_BPM = 100
CRITICAL_BPM = 120

NORMAL_SPO2 = 95
WARNING_SPO2 = 92
CRITICAL_SPO2 = 90

MAX_SCORE = 10


# ============================================================
# HELPER FUNCTION
# ============================================================

def _status(
    value,
    normal_text="",
    warning_text="",
    danger_text="",
    warning=False,
    danger=False
):

    if danger:

        return {

            "value": value,

            "state": "danger",

            "text": danger_text

        }

    if warning:

        return {

            "value": value,

            "state": "warning",

            "text": warning_text

        }

    return {

        "value": value,

        "state": "normal",

        "text": normal_text

    }


# ============================================================
# AI DOCTOR
# ============================================================

def doctor_message(level):

    messages = {

        "NORMAL":

        "Patient is healthy. All vital signs are within the safe operating range.",

        "LOW":

        "Minor abnormalities detected. Continue observation.",

        "MEDIUM":

        "Patient requires regular monitoring. Some vital signs need attention.",

        "HIGH":

        "Patient condition is unstable. Immediate caregiver attention is recommended.",

        "CRITICAL":

        "Emergency condition detected. Immediate medical assistance is required."

    }

    return messages.get(level,"No diagnosis available.")


# ============================================================
# AI FUTURE PREDICTION
# ============================================================

def future_prediction(level):

    if level=="NORMAL":

        return "Patient is expected to remain stable for the next monitoring cycle."

    elif level=="LOW":

        return "Health condition should remain stable with regular observation."

    elif level=="MEDIUM":

        return "Vital signs should be monitored closely over the next few minutes."

    elif level=="HIGH":

        return "Patient condition may worsen without prompt medical attention."

    else:

        return "Immediate intervention is required to prevent further complications."


# ============================================================
# NEXT ACTION
# ============================================================

def next_action(level):

    actions={

        "NORMAL":
        "Continue routine health monitoring.",

        "LOW":
        "Recheck all sensors after 5 minutes.",

        "MEDIUM":
        "Observe the patient continuously and inform family members.",

        "HIGH":
        "Contact the caregiver and prepare to visit the hospital.",

        "CRITICAL":
        "Call emergency medical services immediately."

    }

    return actions[level]


# ============================================================
# HEALTH SCORE
# ============================================================

def calculate_health_score(score):

    health_score = 100 - (score * 10)

    if health_score < 0:

        health_score = 0

    if health_score > 100:

        health_score = 100

    return health_score


# ============================================================
# AI CONFIDENCE
# ============================================================

def ai_confidence(data):

    confidence = 100

    if not data.get("finger_detected"):

        confidence -= 15

    if not data.get("mpu_ready",True):

        confidence -= 10

    if data.get("latitude") is None:

        confidence -= 5

    if confidence < 60:

        confidence = 60

    return confidence


# ============================================================
# START AI ANALYSIS
# ============================================================

def analyze_health(data):

    heart_rate = data.get("heart_rate")

    spo2 = data.get("spo2")

    temperature = data.get("temperature")

    finger_detected = bool(data.get("finger_detected"))

    fall_detected = bool(data.get("fall_detected"))

    sos = bool(data.get("sos"))

    mpu_ready = data.get("mpu_ready",True)

    acc_magnitude = data.get("acc_magnitude",0)

    gyro_magnitude = data.get("gyro_magnitude",0)

    observations=[]

    risks=[]

    recommendations=[]

    priority_actions=[]

    vital_cards={}

    score=0
        # ============================================================
    # TEMPERATURE AI
    # ============================================================

    if temperature is None:

        vital_cards["temperature"] = _status(
            "--",
            "Temperature unavailable."
        )

        observations.append(
            "Temperature sensor data not received."
        )

    elif temperature >= DANGER_TEMP:

        vital_cards["temperature"] = _status(
            temperature,
            danger_text="Very High Body Temperature",
            danger=True
        )

        risks.append(
            "High fever detected."
        )

        recommendations.append(
            "Move the patient to a cool place and seek immediate medical attention."
        )

        priority_actions.append(
            "Check temperature again within 2 minutes."
        )

        score += 4

    elif temperature >= WARNING_TEMP:

        vital_cards["temperature"] = _status(
            temperature,
            warning_text="Body Temperature Slightly High",
            warning=True
        )

        risks.append(
            "Body temperature is above the normal range."
        )

        recommendations.append(
            "Keep the patient hydrated and continue monitoring."
        )

        score += 2

    else:

        vital_cards["temperature"] = _status(
            temperature,
            normal_text="Body Temperature Normal"
        )



    # ============================================================
    # FINGER DETECTION
    # ============================================================

    if not finger_detected:

        vital_cards["heart_rate"] = _status(
            "--",
            warning_text="Finger Not Detected",
            warning=True
        )

        vital_cards["spo2"] = _status(
            "--",
            warning_text="Finger Not Detected",
            warning=True
        )

        observations.append(
            "MAX30102 sensor cannot measure without proper finger contact."
        )

        recommendations.append(
            "Place the finger correctly on the MAX30102 sensor."
        )



    else:

        # ========================================================
        # HEART RATE AI
        # ========================================================

        if heart_rate is None:

            vital_cards["heart_rate"] = _status(
                "--",
                warning_text="Waiting for Heart Rate",
                warning=True
            )

        elif heart_rate >= CRITICAL_BPM:

            vital_cards["heart_rate"] = _status(
                heart_rate,
                danger_text="Critical Heart Rate",
                danger=True
            )

            risks.append(
                "Heart rate is critically high."
            )

            recommendations.append(
                "Allow the patient to rest and seek medical assistance immediately."
            )

            priority_actions.append(
                "Recheck heart rate within one minute."
            )

            score += 4

        elif heart_rate >= HIGH_BPM:

            vital_cards["heart_rate"] = _status(
                heart_rate,
                warning_text="Heart Rate High",
                warning=True
            )

            risks.append(
                "Heart rate is above the configured threshold."
            )

            recommendations.append(
                "Observe the patient and continue monitoring."
            )

            score += 2

        elif heart_rate <= LOW_BPM:

            vital_cards["heart_rate"] = _status(
                heart_rate,
                warning_text="Heart Rate Low",
                warning=True
            )

            risks.append(
                "Heart rate is below the normal range."
            )

            recommendations.append(
                "Ensure the patient is conscious and comfortable."
            )

            score += 2

        else:

            vital_cards["heart_rate"] = _status(
                heart_rate,
                normal_text="Heart Rate Normal"
            )



        # ========================================================
        # SpO2 AI
        # ========================================================

        if spo2 is None:

            vital_cards["spo2"] = _status(
                "--",
                warning_text="Waiting for SpO₂",
                warning=True
            )

        elif spo2 <= CRITICAL_SPO2:

            vital_cards["spo2"] = _status(
                spo2,
                danger_text="Critical Oxygen Level",
                danger=True
            )

            risks.append(
                "Blood oxygen level is critically low."
            )

            recommendations.append(
                "Check breathing and seek emergency medical care."
            )

            priority_actions.append(
                "Verify sensor reading immediately."
            )

            score += 5

        elif spo2 < NORMAL_SPO2:

            vital_cards["spo2"] = _status(
                spo2,
                warning_text="SpO₂ Below Normal",
                warning=True
            )

            risks.append(
                "Blood oxygen level is slightly below normal."
            )

            recommendations.append(
                "Monitor oxygen level continuously."
            )

            score += 3

        else:

            vital_cards["spo2"] = _status(
                spo2,
                normal_text="Healthy Oxygen Level"
            )
            # ============================================================
    # FALL DETECTION AI
    # ============================================================

    if not mpu_ready:

        vital_cards["motion"] = _status(

            "ERROR",

            warning_text="MPU6050 Not Responding",

            warning=True

        )

        observations.append(

            "Motion sensor is unavailable."

        )

        recommendations.append(

            "Check MPU6050 wiring and restart the device."

        )

    elif fall_detected:

        vital_cards["motion"] = _status(

            "FALL",

            danger_text="Fall Detected",

            danger=True

        )

        risks.append(

            "Possible accidental fall detected."

        )

        observations.append(

            f"Acceleration = {acc_magnitude:.2f} g | Gyroscope = {gyro_magnitude:.2f}"

        )

        recommendations.append(

            "Immediately check the patient's condition."

        )

        priority_actions.append(

            "Notify caregiver immediately."

        )

        score += 6

    else:

        vital_cards["motion"] = _status(

            "SAFE",

            normal_text="No Fall Detected"

        )


    # ============================================================
    # SOS BUTTON AI
    # ============================================================

    if sos:

        risks.append(

            "Emergency SOS button pressed."

        )

        observations.append(

            "Manual emergency request received."

        )

        recommendations.append(

            "Contact family members immediately."

        )

        priority_actions.append(

            "Open GPS location and dispatch help."

        )

        score += 6


    # ============================================================
    # LIMIT RISK SCORE
    # ============================================================

    if score > MAX_SCORE:

        score = MAX_SCORE


    # ============================================================
    # AI RISK LEVEL
    # ============================================================

    if score >= 9:

        risk_level = "CRITICAL"

        emergency_type = "Immediate Medical Emergency"

    elif score >= 6:

        risk_level = "HIGH"

        emergency_type = "High Risk"

    elif score >= 3:

        risk_level = "MEDIUM"

        emergency_type = "Needs Continuous Monitoring"

    elif score >= 1:

        risk_level = "LOW"

        emergency_type = "Minor Warning"

    else:

        risk_level = "NORMAL"

        emergency_type = "Healthy"


    # ============================================================
    # DEFAULT VALUES
    # ============================================================

    if len(risks) == 0:

        risks.append(

            "All monitored parameters are within the safe range."

        )

    if len(observations) == 0:

        observations.append(

            "No abnormal sensor activity detected."

        )

    if len(recommendations) == 0:

        recommendations.append(

            "Continue regular monitoring."

        )

    if len(priority_actions) == 0:

        priority_actions.append(

            "No immediate action required."

        )


    # ============================================================
    # AI HEALTH SCORE
    # ============================================================

    health_score = calculate_health_score(score)


    # ============================================================
    # AI CONFIDENCE
    # ============================================================

    confidence = ai_confidence(data)


    # ============================================================
    # AI DOCTOR
    # ============================================================

    doctor = {

        "name": "AI Health Assistant",

        "diagnosis": doctor_message(risk_level),

        "prediction": future_prediction(risk_level),

        "next_action": next_action(risk_level),

        "health_score": health_score,

        "confidence": confidence

    }


    # ============================================================
    # HEALTH SUMMARY
    # ============================================================

    summary = " ".join(risks)
        # ============================================================
    # EMERGENCY LEVEL
    # ============================================================

    if risk_level == "NORMAL":

        emergency_level = 0

    elif risk_level == "LOW":

        emergency_level = 1

    elif risk_level == "MEDIUM":

        emergency_level = 2

    elif risk_level == "HIGH":

        emergency_level = 3

    else:

        emergency_level = 4


    # ============================================================
    # HEALTH METER
    # ============================================================

    if health_score >= 90:

        health_meter = "EXCELLENT"

    elif health_score >= 75:

        health_meter = "GOOD"

    elif health_score >= 60:

        health_meter = "FAIR"

    elif health_score >= 40:

        health_meter = "POOR"

    else:

        health_meter = "CRITICAL"


    # ============================================================
    # RECOVERY PLAN
    # ============================================================

    recovery_plan = []

    if risk_level == "NORMAL":

        recovery_plan = [

            "Continue regular monitoring.",

            "Maintain a healthy diet.",

            "Drink sufficient water.",

            "Perform light physical activity."

        ]

    elif risk_level == "LOW":

        recovery_plan = [

            "Observe patient every 10 minutes.",

            "Provide water and rest.",

            "Repeat sensor measurements."

        ]

    elif risk_level == "MEDIUM":

        recovery_plan = [

            "Monitor patient continuously.",

            "Inform caregiver.",

            "Repeat measurements every 5 minutes."

        ]

    elif risk_level == "HIGH":

        recovery_plan = [

            "Keep patient under observation.",

            "Contact family immediately.",

            "Prepare for hospital visit."

        ]

    else:

        recovery_plan = [

            "Call emergency services.",

            "Share GPS location.",

            "Provide first aid if trained.",

            "Transport patient to hospital immediately."

        ]


    # ============================================================
    # DOCTOR NOTES
    # ============================================================

    doctor_notes = {

        "doctor": "AI Health Assistant",

        "diagnosis": doctor["diagnosis"],

        "prediction": doctor["prediction"],

        "next_action": doctor["next_action"],

        "health_meter": health_meter,

        "health_score": health_score,

        "confidence": confidence,

        "emergency_level": emergency_level

    }


    # ============================================================
    # AI MEDICAL REPORT
    # ============================================================

    medical_report = {

        "title": "AI Medical Report",

        "overall_condition": risk_level,

        "health_score": health_score,

        "health_meter": health_meter,

        "confidence": confidence,

        "doctor": doctor_notes,

        "summary": summary,

        "recommendation": recommendations,

        "priority_actions": priority_actions,

        "recovery_plan": recovery_plan,

        "generated_by": "AI Health Assistant",

        "version": "2.0"

    }


    # ============================================================
    # RETURN
    # ============================================================

    return {

        "risk_level": risk_level,

        "risk_score": score,

        "health_score": health_score,

        "health_meter": health_meter,

        "confidence": confidence,

        "emergency_level": emergency_level,

        "emergency_type": emergency_type,

        "summary": summary,

        "doctor": doctor,

        "medical_report": medical_report,

        "recommendations": recommendations,

        "priority_actions": priority_actions,

        "observations": observations,

        "risks": risks,

        "recovery_plan": recovery_plan,

        "vitals": vital_cards

    }
