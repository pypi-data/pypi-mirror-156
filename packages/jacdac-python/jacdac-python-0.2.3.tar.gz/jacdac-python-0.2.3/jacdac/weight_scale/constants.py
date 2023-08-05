# Autogenerated constants for Weight Scale service
from enum import IntEnum
from jacdac.constants import *
from jacdac.system.constants import *
JD_SERVICE_CLASS_WEIGHT_SCALE = const(0x1f4d5040)


class WeightScaleVariant(IntEnum):
    BODY = const(0x1)
    FOOD = const(0x2)
    JEWELRY = const(0x3)


JD_WEIGHT_SCALE_REG_WEIGHT = const(JD_REG_READING)
JD_WEIGHT_SCALE_REG_WEIGHT_ERROR = const(JD_REG_READING_ERROR)
JD_WEIGHT_SCALE_REG_ZERO_OFFSET = const(0x80)
JD_WEIGHT_SCALE_REG_GAIN = const(0x81)
JD_WEIGHT_SCALE_REG_MAX_WEIGHT = const(JD_REG_MAX_READING)
JD_WEIGHT_SCALE_REG_MIN_WEIGHT = const(JD_REG_MIN_READING)
JD_WEIGHT_SCALE_REG_WEIGHT_RESOLUTION = const(JD_REG_READING_RESOLUTION)
JD_WEIGHT_SCALE_REG_VARIANT = const(JD_REG_VARIANT)
JD_WEIGHT_SCALE_CMD_CALIBRATE_ZERO_OFFSET = const(0x80)
JD_WEIGHT_SCALE_CMD_CALIBRATE_GAIN = const(0x81)
JD_WEIGHT_SCALE_PACK_FORMATS = {
    JD_WEIGHT_SCALE_REG_WEIGHT: "u16.16",
    JD_WEIGHT_SCALE_REG_WEIGHT_ERROR: "u16.16",
    JD_WEIGHT_SCALE_REG_ZERO_OFFSET: "u16.16",
    JD_WEIGHT_SCALE_REG_GAIN: "u16.16",
    JD_WEIGHT_SCALE_REG_MAX_WEIGHT: "u16.16",
    JD_WEIGHT_SCALE_REG_MIN_WEIGHT: "u16.16",
    JD_WEIGHT_SCALE_REG_WEIGHT_RESOLUTION: "u16.16",
    JD_WEIGHT_SCALE_REG_VARIANT: "u8",
    JD_WEIGHT_SCALE_CMD_CALIBRATE_GAIN: "u22.10"
}
