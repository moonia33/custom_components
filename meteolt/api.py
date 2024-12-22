"""API client for Meteo.lt."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
import pytz
from typing import Any, Dict, List, Optional

import aiohttp
import async_timeout

from .const import (
    API_BASE_URL,
    PLACES_ENDPOINT,
    STATIONS_ENDPOINT,
    HYDRO_STATIONS_ENDPOINT,
    TIMEZONE,
)

_LOGGER = logging.getLogger(__name__)


class MeteoLTApiError(Exception):
    """Base exception for API errors."""


class MeteoLTApiConnectionError(MeteoLTApiError):
    """Error when communicating with the API."""


class MeteoLTApiAuthError(MeteoLTApiError):
    """Error when API request is blocked (rate limit)."""


class MeteoLTApiNotFoundError(MeteoLTApiError):
    """Error when resource is not found."""


def convert_to_local_time(timestamp_str: str) -> datetime:
    """Convert UTC timestamp string to local datetime object."""
    utc_dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    utc_dt = pytz.utc.localize(utc_dt)
    local_tz = pytz.timezone(TIMEZONE)
    return utc_dt.astimezone(local_tz)


class MeteoLTApiClient:
    """API client for Meteo.lt."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._places_cache: Optional[List[Dict[str, Any]]] = None
        self._stations_cache: Optional[List[Dict[str, Any]]] = None
        self._hydro_stations_cache: Optional[List[Dict[str, Any]]] = None

    async def _api_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
    ) -> Any:
        """Make an API request."""
        url = f"{API_BASE_URL}{endpoint}"

        try:
            async with async_timeout.timeout(10):
                async with self._session.request(
                    method,
                    url,
                    params=params,
                ) as response:
                    if response.status == 404:
                        raise MeteoLTApiNotFoundError("Resource not found")
                    elif response.status == 429:
                        raise MeteoLTApiAuthError("API rate limit exceeded")
                    elif response.status >= 500:
                        raise MeteoLTApiConnectionError(
                            f"Server error: {response.status}")

                try:
                    response.raise_for_status()
                    data = await response.json()

                    # Convert timestamps to local time if present
                    if isinstance(data, dict):
                        if "forecastTimestamps" in data:
                            for item in data["forecastTimestamps"]:
                                if "forecastTimeUtc" in item:
                                    item["forecastTime"] = convert_to_local_time(
                                        item["forecastTimeUtc"]).isoformat()

                        if "observations" in data:
                            for item in data["observations"]:
                                if "observationTimeUtc" in item:
                                    item["observationTime"] = convert_to_local_time(
                                        item["observationTimeUtc"]).isoformat()

                    return data

                except aiohttp.ContentTypeError as err:
                    raise MeteoLTApiError("Invalid response format") from err

        except asyncio.TimeoutError as exception:
            raise MeteoLTApiError("Timeout error") from exception
        except aiohttp.ClientError as exception:
            raise MeteoLTApiError("Communication error") from exception

    async def get_places(self, force_update: bool = False) -> List[Dict[str, Any]]:
        """Get list of places."""
        if self._places_cache is None or force_update:
            data = await self._api_request(PLACES_ENDPOINT)
            # Filter only Lithuanian places
            self._places_cache = [
                place for place in data if place.get("countryCode") == "LT"
            ]
        return self._places_cache

    async def get_stations(self, force_update: bool = False) -> List[Dict[str, Any]]:
        """Get list of stations."""
        if self._stations_cache is None or force_update:
            self._stations_cache = await self._api_request(STATIONS_ENDPOINT)
        return self._stations_cache

    async def get_hydro_stations(self, force_update: bool = False) -> List[Dict[str, Any]]:
        """Get list of hydro stations."""
        if self._hydro_stations_cache is None or force_update:
            self._hydro_stations_cache = await self._api_request(HYDRO_STATIONS_ENDPOINT)
        return self._hydro_stations_cache

    async def get_place_forecast(self, place_code: str) -> Dict[str, Any]:
        """Get forecast for a specific place."""
        endpoint = f"{PLACES_ENDPOINT}/{place_code}/forecasts/long-term"
        return await self._api_request(endpoint)

    async def get_station_observations(
        self,
        station_code: str,
        date: str = "latest",
    ) -> Dict[str, Any]:
        """Get observations for a specific station."""
        endpoint = f"{STATIONS_ENDPOINT}/{station_code}/observations/{date}"
        return await self._api_request(endpoint)

    async def get_hydro_station_observations(
        self,
        station_code: str,
        observation_type: str = "measured",
        date: str = "latest",
    ) -> Dict[str, Any]:
        """Get hydro observations for a specific station."""
        endpoint = f"{HYDRO_STATIONS_ENDPOINT}/{station_code}/observations/{observation_type}/{date}"
        return await self._api_request(endpoint)

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._places_cache = None
        self._stations_cache = None
        self._hydro_stations_cache = None
