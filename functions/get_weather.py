# hone badna na3mil function bte5od lat w long w bta3mil call lal api w bta3mil return la kam sha8le 5asa bel weather
# l api howe https://openweathermap.org/api

# https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={your_api_key}

import os
import requests
from datetime import date, datetime, timedelta, timezone
from google.genai import types
from dotenv import load_dotenv
from typing import Union

load_dotenv()


def get_historical_weather(lat: float, lon: float, target_date: date):
    METEOSTAT_API_KEY = os.environ.get("METEOSTAT_API_KEY")

    url = "https://meteostat.p.rapidapi.com/point/daily"

    start_str = target_date.strftime("%Y-%m-%d")
    end_str = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "lat": lat,
        "lon": lon,
        "start": start_str,
        "end": end_str
    }

    headers = {
        "x-rapidapi-key": METEOSTAT_API_KEY,
        "x-rapidapi-host": "meteostat.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data.get("data"):
        return {"error": "No historical data for that date"}

    day = data["data"][0]

    tavg = day.get("tavg")
    if tavg is not None:
        temp = tavg
    else:
        tmin = day.get("tmin")
        tmax = day.get("tmax")
        temp = (tmin + tmax) / 2 if tmin is not None and tmax is not None else None

    precip = day.get("prcp", 0)
    snow = day.get("snow", 0)

    return {
        "source": "meteostat",
        "location": f"{lat},{lon}",
        "temp": temp,
        "feels_like": None,
        "humidity": day.get("rhum"),
        "description": "historical weather",
        "wind_speed": day.get("wspd"),
        "clouds": None,
        "precip": precip,
        "snow": snow,
        "time": day.get("date")
    }


def get_current_weather(lat: float, lon: float):
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
    url = "https://api.openweathermap.org/data/2.5/weather"
    # aw hek = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={your_api_key}"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    data = response.json()

    rain = data.get("rain", {})
    snow_data = data.get("snow", {})
    precip = rain.get("1h") or rain.get("3h") or 0
    snow = snow_data.get("1h") or snow_data.get("3h") or 0

    return {
        "source": "openweather_current",
        "location": data.get("name"),
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "clouds": data["clouds"]["all"],
        "precip": precip,
        "snow": snow,
        "time": datetime.fromtimestamp(data["dt"], tz=timezone.utc).isoformat()
    }


def get_forecast_weather(lat: float, lon: float, target_date: date):
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    data = response.json()

    date_str = target_date.strftime("%Y-%m-%d")

    # Filter forecast entries for that specific date
    slots = [item for item in data["list"] if item["dt_txt"].startswith(date_str)]

    if not slots:
        return {"error": "No forecast data for that date"}

    # simple choice: take middle of the day (around 12:00)
    chosen = slots[len(slots) // 2]

    rain = chosen.get("rain", {})
    snow_data = chosen.get("snow", {})
    precip = rain.get("3h") or rain.get("1h") or 0
    snow = snow_data.get("3h") or snow_data.get("1h") or 0

    return {
        "source": "openweather_forecast",
        "location": data.get("city", {}).get("name"),
        "temp": chosen["main"]["temp"],
        "feels_like": chosen["main"]["feels_like"],
        "humidity": chosen["main"]["humidity"],
        "description": chosen["weather"][0]["description"],
        "wind_speed": chosen["wind"]["speed"],
        "clouds": chosen["clouds"]["all"],
        "precip": precip,
        "snow": snow,
        "time": chosen["dt_txt"]
    }


def get_weather(lat: float, lon: float, target_date: Union[str, date, None]):
    # If no date provided → assume today
    if target_date is None:
        target = date.today()

    # If it's a string, interpret it
    elif isinstance(target_date, str):
        text = target_date.strip().lower()

        if text == "today":
            target = date.today()
        elif text == "tomorrow":
            target = date.today() + timedelta(days=1)
        elif text.startswith("in ") and text.endswith(" days"):
            # e.g. "in 3 days"
            try:
                n = int(text[3:-5].strip())
                target = date.today() + timedelta(days=n)
            except ValueError:
                # fall back to ISO parsing
                target = date.fromisoformat(target_date)
        else:
            # Assume ISO format 'YYYY-MM-DD'
            target = date.fromisoformat(target_date)

    # If it's already a date object
    elif isinstance(target_date, date):
        target = target_date
    else:
        return {"error": f"Unsupported target_date type: {type(target_date)}"}

    today = date.today()

    # ✅ use `target`, not `target_date`
    if target < today:
        return get_historical_weather(lat, lon, target)

    elif target == today:
        return get_current_weather(lat, lon)

    elif target <= today + timedelta(days=5):
        return get_forecast_weather(lat, lon, target)

    else:
        return {"error": "Forecast beyond 5 days not available."}


schema_get_weather = types.FunctionDeclaration(
    name="get_weather",
    description="Gets weather information like temperature of a specific location.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "lat": types.Schema(
                type=types.Type.NUMBER,
                description="Latitude of the location in decimal degrees."
            ),
            "lon": types.Schema(
                type=types.Type.NUMBER,
                description="Longitude of the location in decimal degrees."
            ),
            "target_date": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Target date for the weather. Can be 'today', 'tomorrow', "
                    "'in N days', or an ISO date 'YYYY-MM-DD'. If omitted, "
                    "today is assumed."
                )
            ),
        },
        required=["lat", "lon"]
    )
)
