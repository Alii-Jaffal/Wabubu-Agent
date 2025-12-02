# hone badna na3mil function bte5od lat w long w bta3mil call lal api w bta3mil return la kam sha8le 5asa bel weather
# l api howe https://openweathermap.org/api

# https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={your_api_key}

import requests
from datetime import date, datetime, timedelta, timezone
from google.genai import types


def get_historical_weather(lat: float, lon: float, target_date: date):
    API_KEY = "c39b37adb6mshba13d2e8386991cp164da7jsn9228d9bf9fcc"
    url = "https://meteostat.p.rapidapi.com/point/daily"

    start_str = target_date.strftime("%Y-%m-%d")
    end_str   = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "lat": lat,
        "lon": lon,
        "start": start_str,
        "end": end_str
    }

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "meteostat.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data.get("data"):
        return {"error": "No historical data for that date"}

    day = data["data"][0]


    temp = day.get("tavg") or (day.get("tmin") + day.get("tmax")) / 2

    return {
        "source": "meteostat",
        "location": f"{lat},{lon}",
        "temp": temp,
        "feels_like": None,
        "humidity": day.get("rhum"),
        "description": "historical weather",
        "wind_speed": day.get("wspd"),
        "clouds": None,
        "time": day.get("date")
    }



def get_current_weather(lat: float, lon: float):
    API_KEY = "6f2af1fd1c88f29a0db45c69bd6327c6"
    url = "https://api.openweathermap.org/data/2.5/weather"
    # aw hek = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={your_api_key}"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    data = response.json()

    return {
        "source": "openweather_current",
        "location": data.get("name"),
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
        "clouds": data["clouds"]["all"],
        "time": datetime.fromtimestamp(data["dt"], tz=timezone.utc).isoformat()
    }



def get_forecast_weather(lat: float, lon: float, target_date: date):
    API_KEY = "6f2af1fd1c88f29a0db45c69bd6327c6"
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
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

    return {
        "source": "openweather_forecast",
        "location": data.get("city", {}).get("name"),
        "temp": chosen["main"]["temp"],
        "feels_like": chosen["main"]["feels_like"],
        "humidity": chosen["main"]["humidity"],
        "description": chosen["weather"][0]["description"],
        "wind_speed": chosen["wind"]["speed"],
        "clouds": chosen["clouds"]["all"],
        "time": chosen["dt_txt"]
    }




def get_weather(lat: float, lon: float, target_date: date):
    today = date.today()

    if target_date < today:
        return get_historical_weather(lat, lon, target_date)

    elif target_date == today:
        return get_current_weather(lat, lon)

    elif target_date <= today + timedelta(days=5):
        return get_forecast_weather(lat, lon, target_date)

    else:
        return {"error": "Forecast beyond 5 days not available."}


schema_get_weather = types.FunctionDeclaration(
    name="get_weather",
    description="Gets weather information like temperature of a specific location",
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
                description="Target date for the weather in ISO format 'YYYY-MM-DD'."
            )
        },
        required=["lat", "lon", "target_date"]
    )
)