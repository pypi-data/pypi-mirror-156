# Autogenerated file. Do not edit.
from jacdac.bus import Bus, Client
from .constants import *
from typing import Optional


class CapacitiveButtonClient(Client):
    """
    A configuration service for a capacitive push-button.
    Implements a client for the `Capacitive Button <https://microsoft.github.io/jacdac-docs/services/capacitivebutton>`_ service.

    """

    def __init__(self, bus: Bus, role: str) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_CAPACITIVE_BUTTON, JD_CAPACITIVE_BUTTON_PACK_FORMATS, role)


    @property
    def threshold(self) -> Optional[float]:
        """
        Indicates the threshold for ``up`` events., _: /
        """
        return self.register(JD_CAPACITIVE_BUTTON_REG_THRESHOLD).float_value(100)

    @threshold.setter
    def threshold(self, value: float) -> None:
        self.register(JD_CAPACITIVE_BUTTON_REG_THRESHOLD).set_values(value / 100)



    def calibrate(self, ) -> None:
        """
        Request to calibrate the capactive. When calibration is requested, the device expects that no object is touching the button. 
        The report indicates the calibration is done.
        """
        self.send_cmd_packed(JD_CAPACITIVE_BUTTON_CMD_CALIBRATE, )
    
