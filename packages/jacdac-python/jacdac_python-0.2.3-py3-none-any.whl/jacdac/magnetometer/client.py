# Autogenerated file. Do not edit.
from jacdac.bus import Bus, SensorClient
from .constants import *
from typing import Optional, Tuple


class MagnetometerClient(SensorClient):
    """
    A 3-axis magnetometer.
    Implements a client for the `Magnetometer <https://microsoft.github.io/jacdac-docs/services/magnetomer>`_ service.

    """

    def __init__(self, bus: Bus, role: str, *, missing_forces_value: Tuple[int, int, int] = None) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_MAGNETOMETER, JD_MAGNETOMETER_PACK_FORMATS, role)
        self.missing_forces_value = missing_forces_value

    @property
    def forces(self) -> Optional[Tuple[int, int, int]]:
        """
        Indicates the current magnetic field on magnetometer.
        For reference: `1 mgauss` is `100 nT` (and `1 gauss` is `100 000 nT`)., x: nT,y: nT,z: nT
        """
        self.refresh_reading()
        return self.register(JD_MAGNETOMETER_REG_FORCES).value(self.missing_forces_value)

    @property
    def forces_error(self) -> Optional[int]:
        """
        (Optional) Absolute estimated error on the readings., _: nT
        """
        return self.register(JD_MAGNETOMETER_REG_FORCES_ERROR).value()


    def calibrate(self, ) -> None:
        """
        Forces a calibration sequence where the user/device
        might have to rotate to be calibrated.
        """
        self.send_cmd_packed(JD_MAGNETOMETER_CMD_CALIBRATE, )
    
