# Autogenerated file. Do not edit.
from jacdac.bus import Bus, SensorClient, EventHandlerFn, UnsubscribeFn
from .constants import *
from typing import Optional


class MotionClient(SensorClient):
    """
    A sensor, typically PIR, that detects object motion within a certain range
    Implements a client for the `Motion <https://microsoft.github.io/jacdac-docs/services/motion>`_ service.

    """

    def __init__(self, bus: Bus, role: str, *, missing_moving_value: bool = None) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_MOTION, JD_MOTION_PACK_FORMATS, role, preferred_interval = 1000)
        self.missing_moving_value = missing_moving_value

    @property
    def moving(self) -> Optional[bool]:
        """
        Reports is movement is currently detected by the sensor., 
        """
        self.refresh_reading()
        return self.register(JD_MOTION_REG_MOVING).bool_value(self.missing_moving_value)

    @property
    def max_distance(self) -> Optional[float]:
        """
        (Optional) Maximum distance where objects can be detected., _: m
        """
        return self.register(JD_MOTION_REG_MAX_DISTANCE).value()

    @property
    def angle(self) -> Optional[int]:
        """
        (Optional) Opening of the field of view, _: °
        """
        return self.register(JD_MOTION_REG_ANGLE).value()

    @property
    def variant(self) -> Optional[MotionVariant]:
        """
        (Optional) Type of physical sensor, 
        """
        return self.register(JD_MOTION_REG_VARIANT).value()

    def on_movement(self, handler: EventHandlerFn) -> UnsubscribeFn:
        """
        A movement was detected.
        """
        return self.on_event(JD_MOTION_EV_MOVEMENT, handler)

    
