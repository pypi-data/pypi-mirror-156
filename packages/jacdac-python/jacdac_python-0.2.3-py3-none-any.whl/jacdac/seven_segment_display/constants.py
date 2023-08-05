# Autogenerated constants for 7-segment display service
from jacdac.constants import *
from jacdac.system.constants import *
JD_SERVICE_CLASS_SEVEN_SEGMENT_DISPLAY = const(0x196158f7)
JD_SEVEN_SEGMENT_DISPLAY_REG_DIGITS = const(JD_REG_VALUE)
JD_SEVEN_SEGMENT_DISPLAY_REG_BRIGHTNESS = const(JD_REG_INTENSITY)
JD_SEVEN_SEGMENT_DISPLAY_REG_DOUBLE_DOTS = const(0x80)
JD_SEVEN_SEGMENT_DISPLAY_REG_DIGIT_COUNT = const(0x180)
JD_SEVEN_SEGMENT_DISPLAY_REG_DECIMAL_POINT = const(0x181)
JD_SEVEN_SEGMENT_DISPLAY_CMD_SET_NUMBER = const(0x80)
JD_SEVEN_SEGMENT_DISPLAY_PACK_FORMATS = {
    JD_SEVEN_SEGMENT_DISPLAY_REG_DIGITS: "b",
    JD_SEVEN_SEGMENT_DISPLAY_REG_BRIGHTNESS: "u0.16",
    JD_SEVEN_SEGMENT_DISPLAY_REG_DOUBLE_DOTS: "u8",
    JD_SEVEN_SEGMENT_DISPLAY_REG_DIGIT_COUNT: "u8",
    JD_SEVEN_SEGMENT_DISPLAY_REG_DECIMAL_POINT: "u8",
    JD_SEVEN_SEGMENT_DISPLAY_CMD_SET_NUMBER: "f64"
}
