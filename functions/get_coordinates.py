# hone badna na3mil function bte5od location:str w bta3mil call lal api w bta3mil return lal lat w long
# l api howe https://nominatim.org/release-docs/develop/api/Overview/

import requests
from google.genai import types

def get_coordinates(location:str):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "MyPythonScript/1.0"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    lat = data[0]["lat"]
    lon = data[0]["lon"]

    return (lat, lon)


schema_get_coordinates = types.FunctionDeclaration(
    name="get_coordinates",
    description="Gets the coordinates of the given location as a tuple (lat, lon).",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "location": types.Schema(
                type=types.Type.STRING,
                description="Name of a place, city, or country."
            )
        },
        required=["location"]
    ),
)