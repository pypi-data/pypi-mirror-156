# Autogenerated file. Do not edit.
from jacdac.bus import Bus, SensorClient
from .constants import *
from typing import Optional


class TemperatureClient(SensorClient):
    """
    A thermometer measuring outside or inside environment.
    Implements a client for the `Temperature <https://microsoft.github.io/jacdac-docs/services/temperature>`_ service.

    """

    def __init__(self, bus: Bus, role: str, *, missing_temperature_value: float = None) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_TEMPERATURE, JD_TEMPERATURE_PACK_FORMATS, role, preferred_interval = 1000)
        self.missing_temperature_value = missing_temperature_value

    @property
    def temperature(self) -> Optional[float]:
        """
        The temperature., _: °C
        """
        self.refresh_reading()
        return self.register(JD_TEMPERATURE_REG_TEMPERATURE).value(self.missing_temperature_value)

    @property
    def min_temperature(self) -> Optional[float]:
        """
        Lowest temperature that can be reported., _: °C
        """
        return self.register(JD_TEMPERATURE_REG_MIN_TEMPERATURE).value()

    @property
    def max_temperature(self) -> Optional[float]:
        """
        Highest temperature that can be reported., _: °C
        """
        return self.register(JD_TEMPERATURE_REG_MAX_TEMPERATURE).value()

    @property
    def temperature_error(self) -> Optional[float]:
        """
        (Optional) The real temperature is between `temperature - temperature_error` and `temperature + temperature_error`., _: °C
        """
        return self.register(JD_TEMPERATURE_REG_TEMPERATURE_ERROR).value()

    @property
    def variant(self) -> Optional[TemperatureVariant]:
        """
        (Optional) Specifies the type of thermometer., 
        """
        return self.register(JD_TEMPERATURE_REG_VARIANT).value()

    
