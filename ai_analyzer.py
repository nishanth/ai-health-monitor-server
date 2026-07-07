def analyze_health(data):
    heart_rate = data.get("heart_rate")
    spo2 = data.get("spo2")
    temperature = data.get("temperature")
    sos = bool(data.get("sos"))
    fall_detected = bool(data.get("fall_detected"))
    finger_detected = bool(data.get("finger_detected"))
    mpu_ready = data.get("mpu_ready", True)

    risks = []
    recommendations = []
    score = 0

    if sos:
        risks.append("Manual SOS emergency is active.")
        recommendations.append("Contact the patient immediately and check their location.")
        score += 5

    if fall_detected:
        risks.append("Fall event detected by the motion sensor.")
        recommendations.append("Check for injury and confirm whether the patient needs help.")
        score += 5

    if temperature is not None:
        if temperature > 38:
            risks.append("Very high body temperature detected.")
            recommendations.append("High fever risk. Medical attention may be needed.")
            score += 4
        elif temperature > 36:
            risks.append("Temperature is above the configured safe limit.")
            recommendations.append("Monitor temperature and hydration.")
            score += 2

    if finger_detected and heart_rate is not None:
        if heart_rate > 120:
            risks.append("Heart rate is critically high.")
            recommendations.append("Ask the patient to rest and seek medical help if symptoms continue.")
            score += 4
        elif heart_rate > 80:
            risks.append("Heart rate is higher than the configured limit.")
            recommendations.append("Continue monitoring heart rate trend.")
            score += 2
        elif heart_rate < 50:
            risks.append("Heart rate is lower than normal.")
            recommendations.append("Check patient responsiveness and comfort.")
            score += 2

    if finger_detected and spo2 is not None:
        if spo2 < 90:
            risks.append("SpO2 is critically low.")
            recommendations.append("Oxygen level is risky. Seek urgent help if reading is stable.")
            score += 5
        elif spo2 < 95:
            risks.append("SpO2 is below normal range.")
            recommendations.append("Recheck finger placement and continue monitoring.")
            score += 3

    if not finger_detected:
        risks.append("Finger is not detected on MAX30102.")
        recommendations.append("Place finger correctly to measure heart rate and SpO2.")

    if not mpu_ready:
        risks.append("MPU6050 is not responding.")
        recommendations.append("Check MPU6050 wiring and I2C address.")

    if score >= 7:
        risk_level = "CRITICAL"
    elif score >= 4:
        risk_level = "HIGH"
    elif score >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "NORMAL"

    if not risks:
        risks.append("All monitored values are currently within the configured range.")
        recommendations.append("Continue normal monitoring.")

    return {
        "risk_level": risk_level,
        "risk_score": score,
        "summary": " ".join(risks),
        "recommendations": recommendations,
        "risks": risks,
    }
