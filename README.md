# AI Health Monitor Flask Server

This folder is ready to deploy as a Render Python web service.

## Render settings

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment variable: `API_KEY=change-this-secret-key`

After deployment, update the ESP32 sketch:

```cpp
const char* renderServerUrl = "https://your-service-name.onrender.com/api/sensor-data";
const char* renderApiKey = "change-this-secret-key";
```

Use the same API key in Render and ESP32.
