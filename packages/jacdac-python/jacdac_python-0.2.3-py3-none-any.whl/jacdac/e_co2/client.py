# Autogenerated file. Do not edit.
from jacdac.bus import Bus, SensorClient
from .constants import *
from typing import Optional


class ECO2Client(SensorClient):
    """
    Measures equivalent CO₂ levels.
    Implements a client for the `Equivalent CO₂ <https://microsoft.github.io/jacdac-docs/services/eco2>`_ service.

    """

    def __init__(self, bus: Bus, role: str, *, missing_e_CO2_value: float = None) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_E_CO2, JD_E_CO2_PACK_FORMATS, role, preferred_interval = 1000)
        self.missing_e_CO2_value = missing_e_CO2_value

    @property
    def e_CO2(self) -> Optional[float]:
        """
        Equivalent CO₂ (eCO₂) readings., _: ppm
        """
        self.refresh_reading()
        return self.register(JD_E_CO2_REG_E_CO2).value(self.missing_e_CO2_value)

    @property
    def e_CO2_error(self) -> Optional[float]:
        """
        (Optional) Error on the reading value., _: ppm
        """
        return self.register(JD_E_CO2_REG_E_CO2_ERROR).value()

    @property
    def min_e_CO2(self) -> Optional[float]:
        """
        Minimum measurable value, _: ppm
        """
        return self.register(JD_E_CO2_REG_MIN_E_CO2).value()

    @property
    def max_e_CO2(self) -> Optional[float]:
        """
        Minimum measurable value, _: ppm
        """
        return self.register(JD_E_CO2_REG_MAX_E_CO2).value()

    @property
    def variant(self) -> Optional[ECO2Variant]:
        """
        (Optional) Type of physical sensor and capabilities., 
        """
        return self.register(JD_E_CO2_REG_VARIANT).value()

    
