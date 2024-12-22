"""Support for Meteo.lt sensors."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Callable, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
import pytz

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    CONDITION_CODES,
    TIMEZONE,
    CONF_STATION,
    CONF_HYDRO_STATION,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteo.lt sensors based on a config entry."""
    # Get coordinators from hass data
    coordinators = hass.data[DOMAIN][entry.entry_id]
    forecast_coordinator = coordinators["forecast_coordinator"]
    observations_coordinator = coordinators["observations_coordinator"]
    hydro_coordinator = coordinators["hydro_coordinator"]

    entities = []

    # Add forecast sensors
    if forecast_coordinator.data.get("forecast"):
        for sensor_type, sensor_info in SENSOR_TYPES.items():
            if sensor_type not in ["water_level", "water_temperature", "water_discharge"]:
                entities.append(
                    MeteoLTSensor(
                        forecast_coordinator,
                        entry,
                        sensor_type,
                        sensor_info,
                        "forecast"
                    )
                )

    # Add observation sensors if station is configured
    if (
        entry.data.get(CONF_STATION) != "none"
        and observations_coordinator.data.get("observations")
    ):
        for sensor_type, sensor_info in SENSOR_TYPES.items():
            if sensor_type not in ["water_level", "water_temperature", "water_discharge"]:
                entities.append(
                    MeteoLTSensor(
                        observations_coordinator,
                        entry,
                        sensor_type,
                        sensor_info,
                        "observations"
                    )
                )

    # Add hydro observation sensors if hydro station is configured
    if (
        entry.data.get(CONF_HYDRO_STATION) != "none"
        and hydro_coordinator.data.get("hydro")
    ):
        for sensor_type, sensor_info in SENSOR_TYPES.items():
            if sensor_type in ["water_level", "water_temperature", "water_discharge"]:
                entities.append(
                    MeteoLTSensor(
                        hydro_coordinator,
                        entry,
                        sensor_type,
                        sensor_info,
                        "hydro"
                    )
                )

    _LOGGER.debug(
        "Adding %d sensors (%d forecast, %d observations, %d hydro)",
        len(entities),
        sum(1 for e in entities if e._data_type == "forecast"),
        sum(1 for e in entities if e._data_type == "observations"),
        sum(1 for e in entities if e._data_type == "hydro"),
    )

    async_add_entities(entities)


class MeteoLTSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a Meteo.lt sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
        sensor_info: dict[str, Any],
        data_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._config_entry = config_entry
        self._sensor_type = sensor_type
        self._sensor_info = sensor_info
        self._data_type = data_type
        self._attr_unique_id = f"{config_entry.entry_id}_{data_type}_{sensor_type}"

        # Set sensor attributes based on sensor type
        self._attr_name = f"{sensor_info['name']} ({data_type.capitalize()})"
        self._attr_native_unit_of_measurement = sensor_info["unit"]
        self._attr_device_class = self._get_device_class()
        self._attr_state_class = self._get_state_class()
        self._attr_icon = sensor_info["icon"]

        # Set device info based on data type
        device_name = config_entry.title
        if data_type == "observations":
            device_name = f"{device_name} - Observations"
        elif data_type == "hydro":
            device_name = f"{device_name} - Hydro"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_{data_type}")},
            name=device_name,
            manufacturer="LHMT",
            model=data_type.capitalize(),
        )

    def _get_device_class(self) -> SensorDeviceClass | None:
        """Get device class based on sensor type."""
        if self._sensor_info["device_class"] == "temperature":
            return SensorDeviceClass.TEMPERATURE
        if self._sensor_info["device_class"] == "pressure":
            return SensorDeviceClass.PRESSURE
        if self._sensor_info["device_class"] == "humidity":
            return SensorDeviceClass.HUMIDITY
        return None

    def _get_state_class(self) -> SensorStateClass | None:
        """Get state class based on sensor type."""
        if self._sensor_info["state_class"] == "measurement":
            return SensorStateClass.MEASUREMENT
        return None

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        try:
            if self._data_type == "forecast":
                data = self.coordinator.data["forecast"]
                if not data or "forecastTimestamps" not in data:
                    return None
                # Get the first forecast timestamp (current conditions)
                current = data["forecastTimestamps"][0]
                value = current.get(self._sensor_info["key"])

                # Translate condition codes to Lithuanian
                if self._sensor_type == "condition" and value:
                    return CONDITION_CODES.get(value, value)
                return value

            if self._data_type == "observations":
                data = self.coordinator.data["observations"]
                if not data or "observations" not in data:
                    return None
                # Get the latest observation
                current = data["observations"][-1]
                value = current.get(self._sensor_info["key"])

                # Translate condition codes to Lithuanian
                if self._sensor_type == "condition" and value:
                    return CONDITION_CODES.get(value, value)
                return value

            if self._data_type == "hydro":
                data = self.coordinator.data["hydro"]
                if not data or "observations" not in data:
                    return None
                # Get the latest hydro observation
                current = data["observations"][-1]
                return current.get(self._sensor_info["key"])

            return None

        except (KeyError, IndexError, TypeError):
            _LOGGER.error(
                "Error getting state for sensor %s from %s data",
                self._sensor_type,
                self._data_type,
            )
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {}

        try:
            if self._data_type == "forecast":
                data = self.coordinator.data["forecast"]
                if data and "forecastCreationTimeUtc" in data:
                    creation_time = datetime.strptime(
                        data["forecastCreationTimeUtc"],
                        "%Y-%m-%d %H:%M:%S"
                    )
                    creation_time = pytz.utc.localize(creation_time)
                    local_time = creation_time.astimezone(
                        pytz.timezone(TIMEZONE))
                    attrs["last_update"] = local_time.isoformat()

            elif self._data_type in ["observations", "hydro"]:
                data = self.coordinator.data.get(self._data_type, {})
                if data and "observations" in data:
                    latest = data["observations"][-1]
                    if observation_time := latest.get("observationTimeUtc"):
                        obs_time = datetime.strptime(
                            observation_time,
                            "%Y-%m-%d %H:%M:%S"
                        )
                        obs_time = pytz.utc.localize(obs_time)
                        local_time = obs_time.astimezone(
                            pytz.timezone(TIMEZONE))
                        attrs["observation_time"] = local_time.isoformat()

                    if self._data_type == "hydro":
                        if water_body := data.get("station", {}).get("waterBody"):
                            attrs["water_body"] = water_body

        except (KeyError, IndexError, TypeError):
            pass

        return attrs
