# Autogenerated file. Do not edit.
from jacdac.bus import Bus, SensorClient
from .constants import *
from typing import Optional


class RotaryEncoderClient(SensorClient):
    """
    An incremental rotary encoder - converts angular motion of a shaft to digital signal.
    Implements a client for the `Rotary encoder <https://microsoft.github.io/jacdac-docs/services/rotaryencoder>`_ service.

    """

    def __init__(self, bus: Bus, role: str, *, missing_position_value: int = None) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_ROTARY_ENCODER, JD_ROTARY_ENCODER_PACK_FORMATS, role)
        self.missing_position_value = missing_position_value

    @property
    def position(self) -> Optional[int]:
        """
        Upon device reset starts at `0` (regardless of the shaft position).
        Increases by `1` for a clockwise "click", by `-1` for counter-clockwise., _: #
        """
        self.refresh_reading()
        return self.register(JD_ROTARY_ENCODER_REG_POSITION).value(self.missing_position_value)

    @property
    def clicks_per_turn(self) -> Optional[int]:
        """
        This specifies by how much `position` changes when the crank does 360 degree turn. Typically 12 or 24., _: #
        """
        return self.register(JD_ROTARY_ENCODER_REG_CLICKS_PER_TURN).value()

    @property
    def clicker(self) -> Optional[bool]:
        """
        (Optional) The encoder is combined with a clicker. If this is the case, the clicker button service
        should follow this service in the service list of the device., 
        """
        return self.register(JD_ROTARY_ENCODER_REG_CLICKER).bool_value()

    
