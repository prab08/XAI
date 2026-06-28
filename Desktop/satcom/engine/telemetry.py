import requests

HUBS = {
    "Beam 1 (New Delhi)": {"lat": 28.61, "lon": 77.20, "base_demand": 250.0, "priority": 1},
    "Beam 2 (Tokyo Hub)": {"lat": 35.67, "lon": 139.65, "base_demand": 180.0, "priority": 2},
    "Beam 3 (London Gate)": {"lat": 51.50, "lon": -0.12, "base_demand": 150.0, "priority": 3},
    "Beam 4 (New York)": {"lat": 40.71, "lon": -74.00, "base_demand": 300.0, "priority": 1}
}

def fetch_live_link_budget():
    """Fetches real-time weather and calculates RF Link Budget degradations."""
    telemetry = {}
    for name, config in HUBS.items():
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={config['lat']}&longitude={config['lon']}&current_weather=true"
            response = requests.get(url, timeout=5).json()
            weather_code = response.get("current_weather", {}).get("weathercode", 0)

            # Link Physics
            if weather_code in [61, 63, 65, 80, 81, 82]:  # Heavy Rain
                rain_fade_db = 6.2
                weather_severity = 3 # High severity for ML
                modcod = "QPSK 3/4"
            elif weather_code in [51, 53, 55, 71, 73, 75]:  # Light Rain/Overcast
                rain_fade_db = 2.5
                weather_severity = 2
                modcod = "16-APSK 2/3"
            else:  # Clear Sky
                rain_fade_db = 0.0
                weather_severity = 1
                modcod = "32-APSK 5/6"
        except Exception:
            rain_fade_db = 0.0
            weather_severity = 1
            modcod = "32-APSK 5/6"

        telemetry[name] = {
            "rain_fade_db": rain_fade_db,
            "weather_severity": weather_severity,
            "modcod": modcod,
            **config
        }
    return telemetry