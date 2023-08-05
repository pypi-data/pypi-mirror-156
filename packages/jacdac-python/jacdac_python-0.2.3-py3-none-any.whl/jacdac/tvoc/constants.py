# Autogenerated constants for Total Volatile organic compound service
from jacdac.constants import *
from jacdac.system.constants import *
JD_SERVICE_CLASS_TVOC = const(0x12a5b597)
JD_TVOC_REG_TVOC = const(JD_REG_READING)
JD_TVOC_REG_TVOC_ERROR = const(JD_REG_READING_ERROR)
JD_TVOC_REG_MIN_TVOC = const(JD_REG_MIN_READING)
JD_TVOC_REG_MAX_TVOC = const(JD_REG_MAX_READING)
JD_TVOC_PACK_FORMATS = {
    JD_TVOC_REG_TVOC: "u22.10",
    JD_TVOC_REG_TVOC_ERROR: "u22.10",
    JD_TVOC_REG_MIN_TVOC: "u22.10",
    JD_TVOC_REG_MAX_TVOC: "u22.10"
}
