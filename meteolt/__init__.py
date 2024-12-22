"""The Meteo.lt integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import MeteoLTApiClient, MeteoLTApiError
from .const import (
    DOMAIN,
    CONF_PLACE,
    CONF_STATION,
    CONF_HYDRO_STATION,
    UPDATE_INTERVAL_FORECAST,
    UPDATE_INTERVAL_OBSERVATIONS,
    UPDATE_INTERVAL_HYDRO,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meteo.lt from a config entry."""
    # Create API client
    session = async_get_clientsession(hass)
    client = MeteoLTApiClient(session)

    # Create data update coordinators
    async def async_update_forecast() -> dict[str, Any]:
        """Fetch forecast data from API."""
        _LOGGER.debug("Updating forecast data")
        try:
            place_code = entry.data[CONF_PLACE]
            forecast = await client.get_place_forecast(place_code)
            return {"forecast": forecast}
        except MeteoLTApiError as err:
            raise UpdateFailed(f"Error fetching forecast data: {err}") from err

    async def async_update_observations() -> dict[str, Any]:
        """Fetch observation data from API."""
        _LOGGER.debug("Updating observation data")
        try:
            station_code = entry.data[CONF_STATION]
            if station_code and station_code != "none":
                observations = await client.get_station_observations(station_code)
                return {"observations": observations}
            return {"observations": None}
        except MeteoLTApiError as err:
            raise UpdateFailed(
                f"Error fetching observation data: {err}") from err

    async def async_update_hydro() -> dict[str, Any]:
        """Fetch hydro data from API."""
        _LOGGER.debug("Updating hydro data")
        try:
            hydro_station = entry.data[CONF_HYDRO_STATION]
            if hydro_station and hydro_station != "none":
                hydro_data = await client.get_hydro_station_observations(
                    hydro_station,
                    observation_type="measured"
                )
                return {"hydro": hydro_data}
            return {"hydro": None}
        except MeteoLTApiError as err:
            raise UpdateFailed(f"Error fetching hydro data: {err}") from err

    # Create coordinators
    forecast_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Meteo.lt forecast {entry.title}",
        update_method=async_update_forecast,
        update_interval=timedelta(seconds=UPDATE_INTERVAL_FORECAST),
    )

    observations_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Meteo.lt observations {entry.title}",
        update_method=async_update_observations,
        update_interval=timedelta(seconds=UPDATE_INTERVAL_OBSERVATIONS),
    )

    hydro_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Meteo.lt hydro {entry.title}",
        update_method=async_update_hydro,
        update_interval=timedelta(seconds=UPDATE_INTERVAL_HYDRO),
    )

    # Fetch initial data
    await forecast_coordinator.async_config_entry_first_refresh()
    await observations_coordinator.async_config_entry_first_refresh()
    await hydro_coordinator.async_config_entry_first_refresh()

    if not forecast_coordinator.last_update_success:
        raise ConfigEntryNotReady("Failed to fetch initial forecast data")

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "forecast_coordinator": forecast_coordinator,
        "observations_coordinator": observations_coordinator,
        "hydro_coordinator": hydro_coordinator,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
