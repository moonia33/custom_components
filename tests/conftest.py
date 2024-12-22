"""Fixtures for Meteo.lt tests."""
from unittest.mock import patch
import pytest
from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

TEST_PLACES_RESPONSE = [
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
]

TEST_STATIONS_RESPONSE = [
    {
        "code": "vilniaus-ams",
        "name": "Vilniaus AMS",
        "coordinates": {
            "latitude": 54.625992,
            "longitude": 25.107064
        }
    }
]

TEST_HYDRO_STATIONS_RESPONSE = [
    {
        "code": "vilniaus-neris-vms",
        "name": "Vilniaus VMS",
        "waterBody": "Neris",
        "coordinates": {
            "latitude": 54.691858,
            "longitude": 25.276258
        }
    }
]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in Home Assistant."""
    yield


@pytest.fixture
def mock_setup_entry():
    """Mock setup entry."""
    with patch(
        "custom_components.meteolt.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_config_flow_places():
    """Mock places for config flow."""
    return TEST_PLACES_RESPONSE


@pytest.fixture
def mock_config_flow_stations():
    """Mock stations for config flow."""
    return TEST_STATIONS_RESPONSE


@pytest.fixture
def mock_config_flow_hydro_stations():
    """Mock hydro stations for config flow."""
    return TEST_HYDRO_STATIONS_RESPONSE


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Create a mock config entry."""
    return ConfigEntry(
        version=1,
        domain="meteolt",
        title="Vilnius",
        data={
            "place": "vilnius",
            "station": "vilniaus-ams",
            "hydro_station": "vilniaus-neris-vms",
        },
        source="user",
        options={},
        entry_id="test",
    )


@pytest.fixture
def mock_forecast_data():
    """Mock forecast data."""
    return {
        "place": {
            "code": "vilnius",
            "name": "Vilnius",
            "coordinates": {"latitude": 54.687157, "longitude": 25.279652},
        },
        "forecastTimestamps": [
            {
                "forecastTimeUtc": "2024-12-22 12:00:00",
                "airTemperature": 20.0,
                "feelsLikeTemperature": 19.0,
                "windSpeed": 3.0,
                "windGust": 5.0,
                "windDirection": 180,
                "cloudCover": 50,
                "seaLevelPressure": 1015,
                "relativeHumidity": 60,
                "totalPrecipitation": 0.0,
                "conditionCode": "clear"
            }
        ]
    }


@pytest.fixture
def mock_observation_data():
    """Mock observation data."""
    return {
        "station": {
            "code": "vilniaus-ams",
            "name": "Vilniaus AMS",
            "coordinates": {"latitude": 54.625992, "longitude": 25.107064},
        },
        "observations": [
            {
                "observationTimeUtc": "2024-12-22 12:00:00",
                "airTemperature": 19.5,
                "feelsLikeTemperature": 18.5,
                "windSpeed": 2.8,
                "windGust": 4.5,
                "windDirection": 175,
                "cloudCover": 45,
                "seaLevelPressure": 1014,
                "relativeHumidity": 65,
                "precipitation": 0.0,
                "conditionCode": "clear"
            }
        ]
    }


@pytest.fixture
def mock_hydro_data():
    """Mock hydro data."""
    return {
        "station": {
            "code": "vilniaus-neris-vms",
            "name": "Vilniaus VMS",
            "waterBody": "Neris",
            "coordinates": {"latitude": 54.691858, "longitude": 25.276258},
        },
        "observations": [
            {
                "observationTimeUtc": "2024-12-22 12:00:00",
                "waterLevel": 123.4,
                "waterTemperature": 15.6
            }
        ]
    }
