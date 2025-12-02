# hone mna3mil test la functions mnektebon w mnet2akad 2non byeshte8lo
# from functions.get_coordinates import get_coordinates
from functions.get_weather import get_historical_weather, get_current_weather, get_forecast_weather, get_weather
from functions.check_sport_suitability.check_sport_suitability import check_sport_suitability
from datetime import date, timedelta


def main():
    # result = get_historical_weather(33.8938, 35.5018, date(2024, 12, 1))
    # result = get_current_weather(33.8938, 35.5018)
    # result = get_forecast_weather(33.8938, 35.5018, date.today() + timedelta(days=2))
    # print(result)
    # sample_weather = {
    #     "temp": 3,
    #     "wind_speed": 3,
    #     "humidity": 50,
    #     "precip": 0,
    #     "uv": 6,
    #     "snow": 5,
    #     "clouds": 20,
    # }

    # result = check_sport_suitability("Football", sample_weather)
    # print(result)    
    pass

if __name__ == "__main__":
    main()