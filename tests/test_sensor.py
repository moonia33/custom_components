"""Test Meteo.lt sensor."""
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import pytest
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_system import METRIC_SYSTEM
from homeassistant.config_entries import MockConfigEntry

from custom_components.meteolt.const import (
    DOMAIN,
    CONF_PLACE,
    CONF_STATION,
    CONF_HYDRO_STATION,
    UPDATE_INTERVAL_FORECAST,
)

# Test data is moved to conftest.py


async def test_sensor_update(hass: HomeAssistant) -> None:
    """Test sensor updates."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PLACE: "vilnius",
            CONF_STATION: "vilniaus-ams",
            CONF_HYDRO_STATION: "vilniaus-neris-vms",
        },
    )

    coordinator_mock = MagicMock()
    coordinator_mock.data = {
        "forecast": {
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
        },
        "observations": None,
        "hydro": None
    }

    with patch(
        "custom_components.meteolt.sensor.DataUpdateCoordinator",
        return_value=coordinator_mock,
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Check initial values
        state = hass.states.get("sensor.temperature_forecast")
        assert state is not None
        assert state.state == "20.0"

        # Update coordinator data
        new_data = {
            "forecast": {
                "place": {
                    "code": "vilnius",
                    "name": "Vilnius",
                    "coordinates": {"latitude": 54.687157, "longitude": 25.279652},
                },
                "forecastTimestamps": [
                    {
                        "forecastTimeUtc": "2024-12-22 13:00:00",
                        "airTemperature": 21.0,
                        "feelsLikeTemperature": 20.0,
                        "windSpeed": 3.5,
                        "windGust": 5.5,
                        "windDirection": 185,
                        "cloudCover": 55,
                        "seaLevelPressure": 1016,
                        "relativeHumidity": 62,
                        "totalPrecipitation": 0.0,
                        "conditionCode": "partly-cloudy"
                    }
                ]
            },
            "observations": None,
            "hydro": None
        }
        coordinator_mock.data = new_data
        await coordinator_mock.async_refresh()
        await hass.async_block_till_done()

        # Check updated values
        state = hass.states.get("sensor.temperature_forecast")
        assert state is not None
        assert state.state == "21.0"


async def test_sensor_creation(hass: HomeAssistant) -> None:
    """Test creation of sensors."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PLACE: "vilnius",
            CONF_STATION: "vilniaus-ams",
            CONF_HYDRO_STATION: "vilniaus-neris-vms",
        },
    )

    coordinator_mock = MagicMock()
    coordinator_mock.data = {
        "forecast": {
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
        },
        "observations": None,
        "hydro": None
    }

    with patch(
        "custom_components.meteolt.sensor.DataUpdateCoordinator",
        return_value=coordinator_mock,
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Check forecast sensors
        state = hass.states.get("sensor.temperature_forecast")
        assert state is not None
        assert state.state == "20.0"

        state = hass.states.get("sensor.wind_speed_forecast")
        assert state is not None
        assert state.state == "3.0"


async def test_sensor_attributes(hass: HomeAssistant) -> None:
    """Test sensor attributes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PLACE: "vilnius",
            CONF_STATION: "vilniaus-ams",
            CONF_HYDRO_STATION: "vilniaus-neris-vms",
        },
    )

    coordinator_mock = MagicMock()
    coordinator_mock.data = {
        "forecast": {
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
        },
        "observations": None,
        "hydro": None
    }

    with patch(
        "custom_components.meteolt.sensor.DataUpdateCoordinator",
        return_value=coordinator_mock,
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Check forecast sensor attributes
        state = hass.states.get("sensor.temperature_forecast")
        assert state is not None
        attrs = state.attributes
        assert attrs.get("unit_of_measurement") == "°C"
        assert attrs.get("device_class") == "temperature"
        assert attrs.get("state_class") == "measurement"
