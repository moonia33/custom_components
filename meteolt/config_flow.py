"""Config flow for Meteo.lt integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from aiohttp import ClientSession

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv

from .api import MeteoLTApiClient, MeteoLTApiError
from .const import DOMAIN, CONF_PLACE, CONF_STATION, CONF_HYDRO_STATION

_LOGGER = logging.getLogger(__name__)


async def get_place_code_from_coordinates(
    hass: HomeAssistant,
    client: MeteoLTApiClient,
    lat: float,
    lon: float
) -> str | None:
    """Get closest place code from coordinates."""
    import math

    def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points."""
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    try:
        _LOGGER.debug("Getting place code for coordinates: %f, %f", lat, lon)
        places = await client.get_places()
        if not places:
            _LOGGER.warning("No places found")
            return None

        closest_place = min(
            places,
            key=lambda x: distance(
                lat, lon,
                x["coordinates"]["latitude"],
                x["coordinates"]["longitude"]
            )
        )
        _LOGGER.debug("Found closest place: %s", closest_place["code"])
        return closest_place["code"]

    except (MeteoLTApiError, KeyError, ValueError) as err:
        _LOGGER.error("Error getting place code from coordinates: %s", err)
        return None


class MeteoLTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meteo.lt."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._client: MeteoLTApiClient | None = None
        self._places: dict[str, str] = {}
        self._stations: dict[str, str] = {}
        self._hydro_stations: dict[str, str] = {}
        self._default_place: str | None = None

    async def _initialize_data(self) -> None:
        """Initialize data from API."""
        if not self._client:
            session = async_get_clientsession(self.hass)
            self._client = MeteoLTApiClient(session)

        # Try to get default place from home coordinates
        if not self._default_place and hasattr(self.hass, "config"):
            if (
                self.hass.config.latitude is not None
                and self.hass.config.longitude is not None
            ):
                self._default_place = await get_place_code_from_coordinates(
                    self.hass,
                    self._client,
                    self.hass.config.latitude,
                    self.hass.config.longitude,
                )
                _LOGGER.debug("Default place from coordinates: %s",
                              self._default_place)

        # Get data from API
        try:
            places = await self._client.get_places()
            stations = await self._client.get_stations()
            hydro_stations = await self._client.get_hydro_stations()

            self._places = {
                place["code"]: place["name"]
                for place in places
            }

            self._stations = {
                station["code"]: station["name"]
                for station in stations
            }

            self._hydro_stations = {
                station["code"]: f"{station['name']} ({station['waterBody']})"
                for station in hydro_stations
            }

            # Add "No station" options
            self._stations["none"] = "Nestebėti meteorologijos stoties"
            self._hydro_stations["none"] = "Nestebėti hidrologijos stoties"

            _LOGGER.debug("Loaded %d places, %d stations, %d hydro stations",
                          len(places), len(stations), len(hydro_stations))

        except MeteoLTApiError as err:
            _LOGGER.error("Failed to initialize data: %s", err)
            raise

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                return self.async_create_entry(
                    title=self._places.get(
                        user_input[CONF_PLACE], user_input[CONF_PLACE]),
                    data=user_input,
                )
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception(
                    "Unexpected exception during config: %s", err)
                errors["base"] = "unknown"

        if not self._places:
            try:
                await self._initialize_data()
            except MeteoLTApiError:
                errors["base"] = "cannot_connect"
                self._places = {}
                self._stations = {}
                self._hydro_stations = {}
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during init: %s", err)
                errors["base"] = "unknown"
                self._places = {}
                self._stations = {}
                self._hydro_stations = {}

        if not self._places:
            # If we still have no places, show manual input form
            _LOGGER.warning("No places available, showing manual input form")
            schema = {
                vol.Required(CONF_PLACE): str,
                vol.Optional(CONF_STATION): str,
                vol.Optional(CONF_HYDRO_STATION): str,
            }
        else:
            # Show dropdown form with available options
            default_place = self._default_place if self._default_place else vol.UNDEFINED
            schema = {
                vol.Required(CONF_PLACE, default=default_place): vol.In(self._places),
                vol.Optional(CONF_STATION, default="none"): vol.In(self._stations),
                vol.Optional(CONF_HYDRO_STATION, default="none"): vol.In(self._hydro_stations),
            }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema),
            errors=errors,
        )
