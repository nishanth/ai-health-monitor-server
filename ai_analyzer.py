def _status(value, normal_text, warning_text, danger_text, warning=False, danger=False):
    if danger:
        return {"value": value, "state": "danger", "text": danger_text}
    if warning:
        return {"value": value, "state": "warning", "text": warning_text}
    return {"value": value, "state": "normal", "text": normal_text}


def analyze_health(data):
    heart_rate = data.get("heart_rate")
    spo2 = data.get("spo2")
    temperature = data.get("temperature")
    sos = bool(data.get("sos"))
    fall_detected = bool(data.get("fall_detected"))
    finger_detected = bool(data.get("finger_detected"))
    mpu_ready = data.get("mpu_ready", True)
    acc_magnitude = data.get("acc_magnitude", 0)
    gyro_magnitude = data.get("gyro_magnitude", 0)

    observations = []
    risks = []
    recommendations = []
    priority_actions = []
    vital_cards = {}
    score = 0

    if sos:
        risks.append("Manual SOS emergency is active.")
        observations.append("The SOS button was pressed by the user.")
        recommendations.append("Call or reach the patient immediately.")
        priority_actions.append("Open the location map and verify patient safety.")
        score += 6

    if fall_detected:
        risks.append("Fall event detected by MPU6050 motion pattern.")
        observations.append(
            f"Motion impact recorded: {acc_magnitude}g acceleration and {gyro_magnitude} dps rotation."
        )
        recommendations.append("Check for injury, dizziness, or unconsciousness.")
        priority_actions.append("Ask someone nearby to physically check the patient.")
        score += 6

    if temperature is None:
        vital_cards["temperature"] = _status("--", "No temperature data", "", "")
    elif temperature >= 38:
        vital_cards["temperature"] = _status(
            temperature,
            "",
            "",
            "Very high temperature. Fever risk is strong.",
            danger=True,
        )
        risks.append("Body temperature is very high.")
        recommendations.append("Move patient to a comfortable place and consider medical support.")
        score += 4
    elif temperature > 36:
        vital_cards["temperature"] = _status(
            temperature,
            "",
            "Temperature is above the configured safe limit.",
            "",
            warning=True,
        )
        risks.append("Temperature is above the configured safe limit.")
        recommendations.append("Monitor temperature and hydration.")
        score += 2
    else:
        vital_cards["temperature"] = _status(
            temperature,
            "Temperature is inside the configured safe range.",
            "",
            "",
        )

    if not finger_detected:
        vital_cards["heart_rate"] = _status("--", "", "Finger not detected.", "", warning=True)
        vital_cards["spo2"] = _status("--", "", "Finger not detected.", "", warning=True)
        observations.append("MAX30102 finger contact is not detected, so HR and SpO2 are unavailable.")
        recommendations.append("Place finger correctly on MAX30102 for reliable HR and SpO2.")
    else:
        if heart_rate is None:
            vital_cards["heart_rate"] = _status("--", "", "Waiting for heart rate.", "", warning=True)
        elif heart_rate > 120:
            vital_cards["heart_rate"] = _status(
                heart_rate,
                "",
                "",
                "Heart rate is critically high.",
                danger=True,
            )
            risks.append("Heart rate is critically high.")
            recommendations.append("Let the patient rest and seek medical help if symptoms continue.")
            score += 4
        elif heart_rate > 80:
            vital_cards["heart_rate"] = _status(
                heart_rate,
                "",
                "Heart rate is higher than the configured limit.",
                "",
                warning=True,
            )
            risks.append("Heart rate is above the configured limit.")
            recommendations.append("Continue monitoring heart rate trend.")
            score += 2
        elif heart_rate < 50:
            vital_cards["heart_rate"] = _status(
                heart_rate,
                "",
                "Heart rate is lower than expected.",
                "",
                warning=True,
            )
            risks.append("Heart rate is low.")
            recommendations.append("Check patient comfort and responsiveness.")
            score += 2
        else:
            vital_cards["heart_rate"] = _status(
                heart_rate,
                "Heart rate is inside the configured range.",
                "",
                "",
            )

        if spo2 is None:
            vital_cards["spo2"] = _status("--", "", "Waiting for SpO2.", "", warning=True)
        elif spo2 < 90:
            vital_cards["spo2"] = _status(
                spo2,
                "",
                "",
                "SpO2 is critically low.",
                danger=True,
            )
            risks.append("Oxygen saturation is critically low.")
            recommendations.append("Recheck sensor contact. If reading is stable, seek urgent help.")
            priority_actions.append("Confirm breathing comfort and oxygen level immediately.")
            score += 5
        elif spo2 < 95:
            vital_cards["spo2"] = _status(
                spo2,
                "",
                "SpO2 is below normal range.",
                "",
                warning=True,
            )
            risks.append("SpO2 is below normal range.")
            recommendations.append("Recheck finger placement and continue monitoring.")
            score += 3
        else:
            vital_cards["spo2"] = _status(spo2, "SpO2 is in a healthy range.", "", "")

    if not mpu_ready:
        vital_cards["motion"] = _status("ERROR", "", "MPU6050 is not responding.", "", warning=True)
        risks.append("MPU6050 is not responding.")
        recommendations.append("Check MPU6050 wiring, power, SDA/SCL, and I2C address.")
    elif fall_detected:
        vital_cards["motion"] = _status("FALL", "", "", "Fall detected.", danger=True)
    else:
        vital_cards["motion"] = _status("STABLE", "No fall pattern detected.", "", "")

    if score >= 9:
        risk_level = "CRITICAL"
        emergency_type = "Immediate attention required"
    elif score >= 6:
        risk_level = "HIGH"
        emergency_type = "High risk condition"
    elif score >= 3:
        risk_level = "MEDIUM"
        emergency_type = "Needs monitoring"
    elif score >= 1:
        risk_level = "LOW"
        emergency_type = "Minor warning"
    else:
        risk_level = "NORMAL"
        emergency_type = "Stable"

    if not risks:
        risks.append("All monitored values are currently within the configured range.")
        observations.append("No emergency condition is active.")
        recommendations.append("Continue normal monitoring.")

    if not priority_actions:
        priority_actions.append("Keep observing the dashboard for live changes.")

    confidence = "High" if data.get("received_at") else "Waiting for device"
    if not finger_detected:
        confidence = "Medium - HR and SpO2 need finger contact"
    if not mpu_ready:
        confidence = "Medium - motion sensor needs checking"

    summary = " ".join(risks)

    return {
        "risk_level": risk_level,
        "risk_score": min(score, 10),
        "emergency_type": emergency_type,
        "confidence": confidence,
        "summary": summary,
        "recommendations": recommendations,
        "priority_actions": priority_actions,
        "observations": observations,
        "risks": risks,
        "vitals": vital_cards,
    }
