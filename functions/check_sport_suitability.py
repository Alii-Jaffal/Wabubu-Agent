from .sports_data import sports
from typing import Dict, Any, Optional
from google.genai import types

def find_sport_by_name(sport_name: str) -> Optional[Dict[str, Any]]:
    sport_name_lower = sport_name.strip().lower()
    for sport in sports:
        if sport["name"].lower() == sport_name_lower:
            return sport
    return None


def check_sport_suitability(sport_name: str, weather: Dict[str, Any]) -> Dict[str, Any]:
    sport = find_sport_by_name(sport_name)
    if not sport:
        return {
            "suitable": False,
            "message": f"Unknown sport: {sport_name}"
        }

    temp = weather.get("temp")
    wind_speed = weather.get("wind_speed")
    humidity = weather.get("humidity")
    precip = weather.get("precip", 0)
    snow = weather.get("snow", 0)
    clouds = weather.get("clouds")

    conditions = sport["conditions"]
    reason = sport["reason"]

    minTemp = conditions.get("minTemp")
    maxTemp = conditions.get("maxTemp")
    maxWind = conditions.get("maxWind")
    maxHumidity = conditions.get("maxHumidity")
    maxPrecip = conditions.get("maxPrecip")
    minSnow = conditions.get("minSnow")
    maxClouds = conditions.get("maxClouds")

    messages = []

    if minTemp is not None and temp is not None and temp < minTemp:
        messages.append(reason.get("tooCold"))

    if maxTemp is not None and temp is not None and temp > maxTemp:
        messages.append(reason.get("tooHot") or reason.get("tooWarm"))

    if maxWind is not None and wind_speed is not None and wind_speed > maxWind:
        messages.append(reason.get("tooWindy"))

    if maxHumidity is not None and humidity is not None and humidity > maxHumidity:
        messages.append(reason.get("tooHumid"))

    if maxPrecip is not None and precip is not None and precip > maxPrecip:
        messages.append(reason.get("tooRainy"))

    if minSnow is not None and (snow is None or snow < minSnow):
        messages.append(reason.get("notEnoughSnow"))

    if maxClouds is not None and clouds is not None and clouds > maxClouds:
        messages.append(reason.get("tooCloudy"))

    if messages:
        return {
            "suitable": False,
            "message": " AND ".join(m for m in messages if m),
            "sport": sport["name"],
        }

    return {
        "suitable": True,
        "message": f"Great weather for {sport['name']}!",
        "sport": sport["name"],
    }


schema_check_sport_suitability = types.FunctionDeclaration(
    name="check_sport_suitability",
    description="Checks if the given weather conditions are suitable for playing a specific sport. Returns whether the sport is suitable and an explanation.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "sport_name": types.Schema(
                type=types.Type.STRING,
                description="The name of the sport to check (e.g., 'Football', 'Tennis', 'Running')."
            ),
            "weather": types.Schema(
                type=types.Type.OBJECT,
                description="A dictionary containing weather data used to evaluate sport suitability.",
                properties={
                    "temp": types.Schema(
                        type=types.Type.NUMBER,
                        description="Temperature in Celsius."
                    ),
                    "wind_speed": types.Schema(
                        type=types.Type.NUMBER,
                        description="Wind speed in m/s."
                    ),
                    "humidity": types.Schema(
                        type=types.Type.NUMBER,
                        description="Relative humidity percentage."
                    ),
                    "precip": types.Schema(
                        type=types.Type.NUMBER,
                        description="Precipitation amount in mm (optional)."
                    ),
                    "snow": types.Schema(
                        type=types.Type.NUMBER,
                        description="Snow amount in mm (optional)."
                    ),
                    "clouds": types.Schema(
                        type=types.Type.NUMBER,
                        description="Cloudiness percentage (0–100)."
                    ),
                },
                required=["temp", "wind_speed", "humidity", "clouds"]
            ),
        },
        required=["sport_name", "weather"]
    )
)
