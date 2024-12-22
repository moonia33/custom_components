"""Test the Meteo.lt config flow."""
from unittest.mock import patch
import pytest

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from custom_components.meteolt.const import DOMAIN, CONF_PLACE, CONF_STATION, CONF_HYDRO_STATION
from custom_components.meteolt.api import MeteoLTApiError

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
    },
    {
        "code": "kaunas",
        "name": "Kaunas",
        "administrativeDivision": "Kauno miestas",
        "countryCode": "LT",
        "coordinates": {
            "latitude": 54.897222,
            "longitude": 23.886111
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
    },
    {
        "code": "kauno-ams",
        "name": "Kauno AMS",
        "coordinates": {
            "latitude": 54.883960,
            "longitude": 23.835980
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
    },
    {
        "code": "kauno-nemunas-vms",
        "name": "Kauno VMS",
        "waterBody": "Nemunas",
        "coordinates": {
            "latitude": 54.882091,
            "longitude": 23.926865
        }
    }
]


async def test_flow_user_init(hass: HomeAssistant) -> None:
    """Test the initialization of the form in the first step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}


async def test_flow_user_complete(hass: HomeAssistant) -> None:
    """Test the full user configuration flow."""
    with patch(
        "custom_components.meteolt.config_flow.get_place_code_from_coordinates",
        return_value="vilnius",
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_places",
        return_value=TEST_PLACES_RESPONSE,
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_stations",
        return_value=TEST_STATIONS_RESPONSE,
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_hydro_stations",
        return_value=TEST_HYDRO_STATIONS_RESPONSE,
    ), patch(
        "custom_components.meteolt.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        assert result["type"] == "form"
        assert result["errors"] == {}

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_PLACE: "vilnius",
                CONF_STATION: "vilniaus-ams",
                CONF_HYDRO_STATION: "vilniaus-neris-vms",
            },
        )
        await hass.async_block_till_done()

        assert result2["type"] == "create_entry"
        assert result2["title"] == "Vilnius"
        assert result2["data"] == {
            CONF_PLACE: "vilnius",
            CONF_STATION: "vilniaus-ams",
            CONF_HYDRO_STATION: "vilniaus-neris-vms",
        }
        assert len(mock_setup_entry.mock_calls) == 1


async def test_flow_user_no_stations(hass: HomeAssistant) -> None:
    """Test configuration flow selecting no stations."""
    with patch(
        "custom_components.meteolt.config_flow.get_place_code_from_coordinates",
        return_value="vilnius",
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_places",
        return_value=TEST_PLACES_RESPONSE,
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_stations",
        return_value=TEST_STATIONS_RESPONSE,
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_hydro_stations",
        return_value=TEST_HYDRO_STATIONS_RESPONSE,
    ), patch(
        "custom_components.meteolt.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_PLACE: "vilnius",
                CONF_STATION: "none",
                CONF_HYDRO_STATION: "none",
            },
        )

        assert result2["type"] == "create_entry"
        assert result2["title"] == "Vilnius"
        assert result2["data"] == {
            CONF_PLACE: "vilnius",
            CONF_STATION: "none",
            CONF_HYDRO_STATION: "none",
        }


async def test_flow_connection_error(hass: HomeAssistant) -> None:
    """Test config flow errors."""
    with patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_places",
        side_effect=MeteoLTApiError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        assert result["type"] == "form"
        assert result["errors"] == {"base": "cannot_connect"}


async def test_flow_places_empty(hass: HomeAssistant) -> None:
    """Test config flow with empty places response."""
    with patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_places",
        return_value=[],
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_stations",
        return_value=[],
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_hydro_stations",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        assert result["type"] == "form"
        assert result["errors"] == {}


async def test_flow_duplicate_error(hass: HomeAssistant) -> None:
    """Test config flow duplicate error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PLACE: "vilnius"},
        title="Vilnius",
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_places",
        return_value=TEST_PLACES_RESPONSE,
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_stations",
        return_value=TEST_STATIONS_RESPONSE,
    ), patch(
        "custom_components.meteolt.api.MeteoLTApiClient.get_hydro_stations",
        return_value=TEST_HYDRO_STATIONS_RESPONSE,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_PLACE: "vilnius",
                CONF_STATION: "vilniaus-ams",
                CONF_HYDRO_STATION: "vilniaus-neris-vms",
            },
        )

        assert result2["type"] == "abort"
        assert result2["reason"] == "already_configured"
