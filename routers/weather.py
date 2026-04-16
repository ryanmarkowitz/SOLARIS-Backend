from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
import openmeteo_requests
import requests_cache
from retry_requests import retry

router = APIRouter()

# GET /weather?lat=52.52&long=13.41
# Returns:
# {
#   "forecast": [
#     {
#       "time": 1743811200,                  (unix timestamp, one entry per hour, 24 total)
#       "cloud_cover_pct": 42,
#       "precip_probability_pct": 15,
#     },
#     ...
#   ],
#   "sunrise": 1743826800,                   (unix timestamp)
#   "sunset":  1743873600                    (unix timestamp)
# }
@router.get("")
async def get_weather(
    long: float,
    lat: float,
    _user=Depends(get_current_user)
):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": ["precipitation_probability", "cloud_cover"],
        "daily": ["sunrise", "sunset"],
        "forecast_days": 1
    }

    try:
        responses = openmeteo.weather_api(url, params = params)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {str(e)}")

    try:
        # parse through hourly responses and return to frontend
        response = responses[0]
        hourly = response.Hourly()
        hourly_per_prob= hourly.Variables(0).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()

        # used to get a timestamp for each hourly forcast
        start = hourly.Time()
        interval = hourly.Interval()

        # get sunrise / sunset times
        daily = response.Daily()
        sunrise = int(daily.Variables(0).ValuesInt64AsNumpy()[0])
        sunset = int(daily.Variables(1).ValuesInt64AsNumpy()[0])

        forecast = []
        for i in range(24):
            timestamp = start + (i * interval)
            forecast.append({
                "time": timestamp,
                "cloud_cover_pct": int(hourly_cloud_cover[i]),
                "precip_probability_pct": int(hourly_per_prob[i]),
            })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse weather response: {str(e)}")

    return {"forecast": forecast, "sunrise": sunrise, "sunset": sunset}