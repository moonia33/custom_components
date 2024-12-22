"""Constants for the Meteo.lt integration."""
from typing import Final
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfLength,
    PERCENTAGE,
    Platform,
)

DOMAIN = "meteolt"
PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_PLACE = "place"
CONF_STATION = "station"
CONF_HYDRO_STATION = "hydro_station"

UPDATE_INTERVAL_FORECAST = 1800  # 30 minutes
UPDATE_INTERVAL_OBSERVATIONS = 3600  # 60 minutes
UPDATE_INTERVAL_HYDRO = 3600  # 60 minutes

# Base API URL
API_BASE_URL = "https://api.meteo.lt/v1"

# API Endpoints
PLACES_ENDPOINT = "/places"
STATIONS_ENDPOINT = "/stations"
HYDRO_STATIONS_ENDPOINT = "/hydro-stations"
FORECASTS_ENDPOINT = "/forecasts"
OBSERVATIONS_ENDPOINT = "/observations"

# Forecast types
FORECAST_TYPE_WEATHER = "weather"
FORECAST_TYPE_HYDRO = "hydro"
FORECAST_TYPES = [FORECAST_TYPE_WEATHER, FORECAST_TYPE_HYDRO]

# Time related
TIMEZONE = "Europe/Vilnius"

# Sensor types
SENSOR_TYPES = {
    # Weather forecast sensors
    "temperature": {
        "key": "airTemperature",
        "name": "Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "feels_like": {
        "key": "feelsLikeTemperature",
        "name": "Feels Like Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "wind_speed": {
        "key": "windSpeed",
        "name": "Wind Speed",
        "unit": UnitOfSpeed.METERS_PER_SECOND,
        "icon": "mdi:weather-windy",
        "device_class": None,
        "state_class": "measurement",
    },
    "wind_gust": {
        "key": "windGust",
        "name": "Wind Gust",
        "unit": UnitOfSpeed.METERS_PER_SECOND,
        "icon": "mdi:weather-windy-variant",
        "device_class": None,
        "state_class": "measurement",
    },
    "wind_direction": {
        "key": "windDirection",
        "name": "Wind Direction",
        "unit": "°",
        "icon": "mdi:compass",
        "device_class": None,
        "state_class": "measurement",
    },
    "cloud_cover": {
        "key": "cloudCover",
        "name": "Cloud Cover",
        "unit": PERCENTAGE,
        "icon": "mdi:weather-cloudy",
        "device_class": None,
        "state_class": "measurement",
    },
    "pressure": {
        "key": "seaLevelPressure",
        "name": "Sea Level Pressure",
        "unit": UnitOfPressure.HPA,
        "icon": "mdi:gauge",
        "device_class": "pressure",
        "state_class": "measurement",
    },
    "humidity": {
        "key": "relativeHumidity",
        "name": "Relative Humidity",
        "unit": PERCENTAGE,
        "icon": "mdi:water-percent",
        "device_class": "humidity",
        "state_class": "measurement",
    },
    "precipitation": {
        "key": "totalPrecipitation",
        "name": "Precipitation",
        "unit": UnitOfLength.MILLIMETERS,
        "icon": "mdi:water",
        "device_class": None,
        "state_class": "measurement",
    },
    "condition": {
        "key": "conditionCode",
        "name": "Condition",
        "unit": None,
        "icon": "mdi:weather-partly-cloudy",
        "device_class": None,
        "state_class": None,
    },
    # Hydro sensors
    "water_level": {
        "key": "waterLevel",
        "name": "Water Level",
        "unit": UnitOfLength.CENTIMETERS,
        "icon": "mdi:waves-arrow-up",
        "device_class": None,
        "state_class": "measurement",
    },
    "water_temperature": {
        "key": "waterTemperature",
        "name": "Water Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "water_discharge": {
        "key": "waterDischarge",
        "name": "Water Discharge",
        "unit": "m³/s",
        "icon": "mdi:waves",
        "device_class": None,
        "state_class": "measurement",
    },
}

# Weather condition codes and translations
CONDITION_CODES = {
    "clear": "Giedra",
    "partly-cloudy": "Mažai debesuota",
    "cloudy-with-sunny-intervals": "Debesuota su pragiedruliais",
    "cloudy": "Debesuota",
    "light-rain": "Nedidelis lietus",
    "rain": "Lietus",
    "heavy-rain": "Smarkus lietus",
    "thunder": "Perkūnija",
    "isolated-thunderstorms": "Trumpas lietus su perkūnija",
    "thunderstorms": "Lietus su perkūnija",
    "heavy-rain-with-thunderstorms": "Smarkus lietus su perkūnija",
    "light-sleet": "Nedidelė šlapdriba",
    "sleet": "Šlapdriba",
    "freezing-rain": "Lijundra",
    "hail": "Kruša",
    "light-snow": "Nedidelis sniegas",
    "snow": "Sniegas",
    "heavy-snow": "Smarkus sniegas",
    "fog": "Rūkas",
    "variable-cloudiness": "Nepastoviai debesuota",
    "rain-showers": "Trumpas lietus",
    "light-rain-at-times": "Protarpiais nedidelis lietus",
    "rain-at-times": "Protarpiais lietus",
    "sleet-showers": "Trumpa šlapdriba",
    "sleet-at-times": "Protarpiais šlapdriba",
    "snow-showers": "Trumpas sniegas",
    "light-snow-at-times": "Protarpiais nedidelis sniegas",
    "snow-at-times": "Protarpiais sniegas",
    "snowstorm": "Pūga",
    "squall": "Škvalas",
}
