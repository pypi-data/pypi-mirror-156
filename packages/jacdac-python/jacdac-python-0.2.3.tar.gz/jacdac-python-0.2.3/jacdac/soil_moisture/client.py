# Autogenerated file. Do not edit.
from jacdac.bus import Bus, SensorClient
from .constants import *
from typing import Optional


class SoilMoistureClient(SensorClient):
    """
    A soil moisture sensor.
    Implements a client for the `Soil moisture <https://microsoft.github.io/jacdac-docs/services/soilmoisture>`_ service.

    """

    def __init__(self, bus: Bus, role: str, *, missing_moisture_value: float = None) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_SOIL_MOISTURE, JD_SOIL_MOISTURE_PACK_FORMATS, role, preferred_interval = 1000)
        self.missing_moisture_value = missing_moisture_value

    @property
    def moisture(self) -> Optional[float]:
        """
        Indicates the wetness of the soil, from `dry` to `wet`., _: /
        """
        self.refresh_reading()
        return self.register(JD_SOIL_MOISTURE_REG_MOISTURE).float_value(self.missing_moisture_value, 100)

    @property
    def moisture_error(self) -> Optional[float]:
        """
        (Optional) The error on the moisture reading., _: /
        """
        return self.register(JD_SOIL_MOISTURE_REG_MOISTURE_ERROR).float_value(100)

    @property
    def variant(self) -> Optional[SoilMoistureVariant]:
        """
        (Optional) Describe the type of physical sensor., 
        """
        return self.register(JD_SOIL_MOISTURE_REG_VARIANT).value()

    
