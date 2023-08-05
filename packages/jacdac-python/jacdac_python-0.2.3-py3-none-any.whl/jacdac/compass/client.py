# Autogenerated file. Do not edit.
from jacdac.bus import Bus, SensorClient
from .constants import *
from typing import Optional


class CompassClient(SensorClient):
    """
    A sensor that measures the heading.
    Implements a client for the `Compass <https://microsoft.github.io/jacdac-docs/services/compass>`_ service.

    """

    def __init__(self, bus: Bus, role: str, *, missing_heading_value: float = None) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_COMPASS, JD_COMPASS_PACK_FORMATS, role, preferred_interval = 1000)
        self.missing_heading_value = missing_heading_value

    @property
    def heading(self) -> Optional[float]:
        """
        The heading with respect to the magnetic north., _: °
        """
        self.refresh_reading()
        return self.register(JD_COMPASS_REG_HEADING).value(self.missing_heading_value)

    @property
    def enabled(self) -> Optional[bool]:
        """
        Turn on or off the sensor. Turning on the sensor may start a calibration sequence., 
        """
        return self.register(JD_COMPASS_REG_ENABLED).bool_value()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self.register(JD_COMPASS_REG_ENABLED).set_values(value)


    @property
    def heading_error(self) -> Optional[float]:
        """
        (Optional) Error on the heading reading, _: °
        """
        return self.register(JD_COMPASS_REG_HEADING_ERROR).value()


    def calibrate(self, ) -> None:
        """
        Starts a calibration sequence for the compass.
        """
        self.send_cmd_packed(JD_COMPASS_CMD_CALIBRATE, )
    
