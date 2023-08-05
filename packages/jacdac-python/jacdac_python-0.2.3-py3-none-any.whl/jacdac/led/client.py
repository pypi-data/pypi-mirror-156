# Autogenerated file. Do not edit.
from jacdac.bus import Bus, Client
from .constants import *
from typing import Optional


class LedClient(Client):
    """
    A controller for small displays of individually controlled RGB LEDs.
     * 
     * This service handles displays with 64 or less LEDs.
     * Use the [LED strip service](/services/ledstrip) for longer light strips.
    Implements a client for the `LED <https://microsoft.github.io/jacdac-docs/services/led>`_ service.

    """

    def __init__(self, bus: Bus, role: str) -> None:
        super().__init__(bus, JD_SERVICE_CLASS_LED, JD_LED_PACK_FORMATS, role)


    @property
    def pixels(self) -> Optional[bytes]:
        """
        A buffer of 24bit RGB color entries for each LED, in R, G, B order.
        When writing, if the buffer is too short, the remaining pixels are set to `#000000`;
        if the buffer is too long, the write may be ignored, or the additional pixels may be ignored., 
        """
        return self.register(JD_LED_REG_PIXELS).value()

    @pixels.setter
    def pixels(self, value: bytes) -> None:
        self.register(JD_LED_REG_PIXELS).set_values(value)


    @property
    def brightness(self) -> Optional[float]:
        """
        Set the luminosity of the strip.
        At `0` the power to the strip is completely shut down., _: /
        """
        return self.register(JD_LED_REG_BRIGHTNESS).float_value(100)

    @brightness.setter
    def brightness(self, value: float) -> None:
        self.register(JD_LED_REG_BRIGHTNESS).set_values(value / 100)


    @property
    def actual_brightness(self) -> Optional[float]:
        """
        This is the luminosity actually applied to the strip.
        May be lower than `brightness` if power-limited by the `max_power` register.
        It will rise slowly (few seconds) back to `brightness` is limits are no longer required., _: /
        """
        return self.register(JD_LED_REG_ACTUAL_BRIGHTNESS).float_value(100)

    @property
    def num_pixels(self) -> Optional[int]:
        """
        Specifies the number of pixels in the strip., _: #
        """
        return self.register(JD_LED_REG_NUM_PIXELS).value()

    @property
    def num_columns(self) -> Optional[int]:
        """
        (Optional) If the LED pixel strip is a matrix, specifies the number of columns., _: #
        """
        return self.register(JD_LED_REG_NUM_COLUMNS).value()

    @property
    def max_power(self) -> Optional[int]:
        """
        (Optional) Limit the power drawn by the light-strip (and controller)., _: mA
        """
        return self.register(JD_LED_REG_MAX_POWER).value()

    @max_power.setter
    def max_power(self, value: int) -> None:
        self.register(JD_LED_REG_MAX_POWER).set_values(value)


    @property
    def leds_per_pixel(self) -> Optional[int]:
        """
        (Optional) If known, specifies the number of LEDs in parallel on this device.
        The actual number of LEDs is `num_pixels * leds_per_pixel`., _: #
        """
        return self.register(JD_LED_REG_LEDS_PER_PIXEL).value()

    @property
    def wave_length(self) -> Optional[int]:
        """
        (Optional) If monochrome LED, specifies the wave length of the LED.
        Register is missing for RGB LEDs., _: nm
        """
        return self.register(JD_LED_REG_WAVE_LENGTH).value()

    @property
    def luminous_intensity(self) -> Optional[int]:
        """
        (Optional) The luminous intensity of all the LEDs, at full brightness, in micro candella., _: mcd
        """
        return self.register(JD_LED_REG_LUMINOUS_INTENSITY).value()

    @property
    def variant(self) -> Optional[LedVariant]:
        """
        (Optional) Specifies the shape of the light strip., 
        """
        return self.register(JD_LED_REG_VARIANT).value()

    
