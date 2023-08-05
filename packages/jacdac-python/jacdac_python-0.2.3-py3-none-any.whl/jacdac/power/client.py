# Autogenerated file. Do not edit.
from jacdac.bus import Bus, SensorClient, EventHandlerFn, UnsubscribeFn
from .constants import *
from typing import Optional


class PowerClient(SensorClient):
    """
    A power-provider service.
    Implements a client for the `Power <https://microsoft.github.io/jacdac-docs/services/power>`_ service.

    """

    def __init__(self, bus: Bus, role: str, *, missing_current_draw_value: int = None) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_POWER, JD_POWER_PACK_FORMATS, role)
        self.missing_current_draw_value = missing_current_draw_value

    @property
    def allowed(self) -> Optional[bool]:
        """
        Can be used to completely disable the service.
        When allowed, the service may still not be providing power, see 
        `power_status` for the actual current state., 
        """
        return self.register(JD_POWER_REG_ALLOWED).bool_value()

    @allowed.setter
    def allowed(self, value: bool) -> None:
        self.register(JD_POWER_REG_ALLOWED).set_values(value)


    @property
    def max_power(self) -> Optional[int]:
        """
        (Optional) Limit the power provided by the service. The actual maximum limit will depend on hardware.
        This field may be read-only in some implementations - you should read it back after setting., _: mA
        """
        return self.register(JD_POWER_REG_MAX_POWER).value()

    @max_power.setter
    def max_power(self, value: int) -> None:
        self.register(JD_POWER_REG_MAX_POWER).set_values(value)


    @property
    def power_status(self) -> Optional[PowerPowerStatus]:
        """
        Indicates whether the power provider is currently providing power (`Powering` state), and if not, why not.
        `Overprovision` means there was another power provider, and we stopped not to overprovision the bus., 
        """
        return self.register(JD_POWER_REG_POWER_STATUS).value()

    @property
    def current_draw(self) -> Optional[int]:
        """
        (Optional) Present current draw from the bus., _: mA
        """
        self.refresh_reading()
        return self.register(JD_POWER_REG_CURRENT_DRAW).value(self.missing_current_draw_value)

    @property
    def battery_voltage(self) -> Optional[int]:
        """
        (Optional) Voltage on input., _: mV
        """
        return self.register(JD_POWER_REG_BATTERY_VOLTAGE).value()

    @property
    def battery_charge(self) -> Optional[float]:
        """
        (Optional) Fraction of charge in the battery., _: /
        """
        return self.register(JD_POWER_REG_BATTERY_CHARGE).float_value(100)

    @property
    def battery_capacity(self) -> Optional[int]:
        """
        (Optional) Energy that can be delivered to the bus when battery is fully charged.
        This excludes conversion overheads if any., _: mWh
        """
        return self.register(JD_POWER_REG_BATTERY_CAPACITY).value()

    @property
    def keep_on_pulse_duration(self) -> Optional[int]:
        """
        (Optional) Many USB power packs need current to be drawn from time to time to prevent shutdown.
        This regulates how often and for how long such current is drawn.
        Typically a 1/8W 22 ohm resistor is used as load. This limits the duty cycle to 10%., _: ms
        """
        return self.register(JD_POWER_REG_KEEP_ON_PULSE_DURATION).value()

    @keep_on_pulse_duration.setter
    def keep_on_pulse_duration(self, value: int) -> None:
        self.register(JD_POWER_REG_KEEP_ON_PULSE_DURATION).set_values(value)


    @property
    def keep_on_pulse_period(self) -> Optional[int]:
        """
        (Optional) Many USB power packs need current to be drawn from time to time to prevent shutdown.
        This regulates how often and for how long such current is drawn.
        Typically a 1/8W 22 ohm resistor is used as load. This limits the duty cycle to 10%., _: ms
        """
        return self.register(JD_POWER_REG_KEEP_ON_PULSE_PERIOD).value()

    @keep_on_pulse_period.setter
    def keep_on_pulse_period(self, value: int) -> None:
        self.register(JD_POWER_REG_KEEP_ON_PULSE_PERIOD).set_values(value)


    def on_power_status_changed(self, handler: EventHandlerFn) -> UnsubscribeFn:
        """
        Emitted whenever `power_status` changes.
        """
        return self.on_event(JD_POWER_EV_POWER_STATUS_CHANGED, handler)


    def shutdown(self, ) -> None:
        """
        Sent by the power service periodically, as broadcast.
        """
        self.send_cmd_packed(JD_POWER_CMD_SHUTDOWN, )
    
