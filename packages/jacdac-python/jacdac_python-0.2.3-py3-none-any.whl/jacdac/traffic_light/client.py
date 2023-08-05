# Autogenerated file. Do not edit.
from jacdac.bus import Bus, Client
from .constants import *
from typing import Optional


class TrafficLightClient(Client):
    """
    Controls a mini traffic with a red, orange and green LED.
    Implements a client for the `Traffic Light <https://microsoft.github.io/jacdac-docs/services/trafficlight>`_ service.

    """

    def __init__(self, bus: Bus, role: str) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_TRAFFIC_LIGHT, JD_TRAFFIC_LIGHT_PACK_FORMATS, role)


    @property
    def red(self) -> Optional[bool]:
        """
        The on/off state of the red light., 
        """
        return self.register(JD_TRAFFIC_LIGHT_REG_RED).bool_value()

    @red.setter
    def red(self, value: bool) -> None:
        self.register(JD_TRAFFIC_LIGHT_REG_RED).set_values(value)


    @property
    def yellow(self) -> Optional[bool]:
        """
        The on/off state of the yellow light., 
        """
        return self.register(JD_TRAFFIC_LIGHT_REG_YELLOW).bool_value()

    @yellow.setter
    def yellow(self, value: bool) -> None:
        self.register(JD_TRAFFIC_LIGHT_REG_YELLOW).set_values(value)


    @property
    def green(self) -> Optional[bool]:
        """
        The on/off state of the green light., 
        """
        return self.register(JD_TRAFFIC_LIGHT_REG_GREEN).bool_value()

    @green.setter
    def green(self, value: bool) -> None:
        self.register(JD_TRAFFIC_LIGHT_REG_GREEN).set_values(value)


    
