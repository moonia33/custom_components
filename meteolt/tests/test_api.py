"""Test the Meteo.lt API client."""
import asyncio
from datetime import datetime
import pytest
from aiohttp import ClientError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.meteolt.api import (
    MeteoLTApiClient,
    MeteoLTApiError,
    MeteoLTApiConnectionError,
    MeteoLTApiAuthError,
    MeteoLTApiNotFoundError,
    convert_to_local_time,
)

TEST_PLACE = "vilnius"
TEST_STATION = "vilniaus-ams"
TEST_HYDRO_STATION = "vilniaus-neris-vms"


async def test_convert_to_local_time():
    """Test UTC to local time conversion."""
    utc_time = "2024-12-22 12:00:00"
    local_time = convert_to_local_time(utc_time)
    assert local_time.hour == 14  # UTC+2
    assert local_time.minute == 0
    assert local_time.second == 0


async def test_api_get_places(hass, aioclient_mock):
    """Test getting places."""
    aioclient_mock.get(
        "https://api.meteo.lt/v1/places",
        json=[
            {
                "code": "vilnius",
                "name": "Vilnius",
                "administrativeDivision": "Vilniaus miestas",
                "countryCode": "LT",
                "coordinates": {
                    "latitude": 54.687157,
                    "longitude": 25.279652
                }
            }
        ],
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)
    places = await client.get_places()

    assert places[0]["code"] == "vilnius"
    assert places[0]["name"] == "Vilnius"
    assert places[0]["countryCode"] == "LT"


async def test_api_get_stations(hass, aioclient_mock):
    """Test getting stations."""
    aioclient_mock.get(
        "https://api.meteo.lt/v1/stations",
        json=[
            {
                "code": "vilniaus-ams",
                "name": "Vilniaus AMS",
                "coordinates": {
                    "latitude": 54.625992,
                    "longitude": 25.107064
                }
            }
        ],
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)
    stations = await client.get_stations()

    assert stations[0]["code"] == "vilniaus-ams"
    assert stations[0]["name"] == "Vilniaus AMS"


async def test_api_get_hydro_stations(hass, aioclient_mock):
    """Test getting hydro stations."""
    aioclient_mock.get(
        "https://api.meteo.lt/v1/hydro-stations",
        json=[
            {
                "code": "vilniaus-neris-vms",
                "name": "Vilniaus VMS",
                "waterBody": "Neris",
                "coordinates": {
                    "latitude": 54.691858,
                    "longitude": 25.276258
                }
            }
        ],
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)
    stations = await client.get_hydro_stations()

    assert stations[0]["code"] == "vilniaus-neris-vms"
    assert stations[0]["name"] == "Vilniaus VMS"
    assert stations[0]["waterBody"] == "Neris"


async def test_api_get_place_forecast(hass, aioclient_mock):
    """Test getting place forecast."""
    aioclient_mock.get(
        f"https://api.meteo.lt/v1/places/{TEST_PLACE}/forecasts/long-term",
        json={
            "place": {
                "code": TEST_PLACE,
                "name": "Vilnius",
            },
            "forecastTimestamps": [
                {
                    "forecastTimeUtc": "2024-12-22 12:00:00",
                    "airTemperature": 20.0,
                }
            ]
        },
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)
    forecast = await client.get_place_forecast(TEST_PLACE)

    assert forecast["place"]["code"] == TEST_PLACE
    assert forecast["forecastTimestamps"][0]["airTemperature"] == 20.0


async def test_api_get_station_observations(hass, aioclient_mock):
    """Test getting station observations."""
    aioclient_mock.get(
        f"https://api.meteo.lt/v1/stations/{TEST_STATION}/observations/latest",
        json={
            "station": {
                "code": TEST_STATION,
                "name": "Vilniaus AMS",
            },
            "observations": [
                {
                    "observationTimeUtc": "2024-12-22 12:00:00",
                    "airTemperature": 18.5,
                }
            ]
        },
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)
    observations = await client.get_station_observations(TEST_STATION)

    assert observations["station"]["code"] == TEST_STATION
    assert observations["observations"][0]["airTemperature"] == 18.5


async def test_api_get_hydro_station_observations(hass, aioclient_mock):
    """Test getting hydro station observations."""
    aioclient_mock.get(
        f"https://api.meteo.lt/v1/hydro-stations/{TEST_HYDRO_STATION}/observations/measured/latest",
        json={
            "station": {
                "code": TEST_HYDRO_STATION,
                "name": "Vilniaus VMS",
                "waterBody": "Neris"
            },
            "observations": [
                {
                    "observationTimeUtc": "2024-12-22 12:00:00",
                    "waterLevel": 123.4,
                    "waterTemperature": 15.6
                }
            ]
        },
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)
    observations = await client.get_hydro_station_observations(TEST_HYDRO_STATION)

    assert observations["station"]["code"] == TEST_HYDRO_STATION
    assert observations["observations"][0]["waterLevel"] == 123.4
    assert observations["observations"][0]["waterTemperature"] == 15.6


async def test_api_rate_limit_error(hass, aioclient_mock):
    """Test API rate limit error handling."""
    aioclient_mock.get(
        "https://api.meteo.lt/v1/places",
        status=429,
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)

    with pytest.raises(MeteoLTApiAuthError):
        await client.get_places()


async def test_api_not_found_error(hass, aioclient_mock):
    """Test API not found error handling."""
    aioclient_mock.get(
        f"https://api.meteo.lt/v1/places/nonexistent/forecasts/long-term",
        status=404,
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)

    with pytest.raises(MeteoLTApiNotFoundError):
        await client.get_place_forecast("nonexistent")


async def test_api_server_error(hass, aioclient_mock):
    """Test API server error handling."""
    aioclient_mock.get(
        "https://api.meteo.lt/v1/places",
        status=500,
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)

    with pytest.raises(MeteoLTApiConnectionError):
        await client.get_places()


async def test_api_timeout_error(hass, aioclient_mock):
    """Test API timeout error handling."""
    aioclient_mock.get(
        "https://api.meteo.lt/v1/places",
        exc=asyncio.TimeoutError
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)

    with pytest.raises(MeteoLTApiError):
        await client.get_places()


async def test_api_connection_error(hass, aioclient_mock):
    """Test API connection error handling."""
    aioclient_mock.get(
        "https://api.meteo.lt/v1/places",
        exc=ClientError
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)

    with pytest.raises(MeteoLTApiError):
        await client.get_places()


async def test_api_cache_behavior(hass, aioclient_mock):
    """Test API caching behavior."""
    aioclient_mock.get(
        "https://api.meteo.lt/v1/places",
        json=[{"code": "vilnius", "name": "Vilnius", "countryCode": "LT"}]
    )

    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)

    # First call should make an API request
    places1 = await client.get_places()
    assert len(aioclient_mock.mock_calls) == 1

    # Second call should use cache
    places2 = await client.get_places()
    assert len(aioclient_mock.mock_calls) == 1

    # Force update should make new API request
    places3 = await client.get_places(force_update=True)
    assert len(aioclient_mock.mock_calls) == 2

    # Clear cache and verify new request
    client.clear_cache()
    places4 = await client.get_places()
    assert len(aioclient_mock.mock_calls) == 3
