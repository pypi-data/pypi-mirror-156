# Autogenerated constants for Matrix Keypad service
from enum import IntEnum
from jacdac.constants import *
from jacdac.system.constants import *
JD_SERVICE_CLASS_MATRIX_KEYPAD = const(0x13062dc8)


class MatrixKeypadVariant(IntEnum):
    MEMBRANE = const(0x1)
    KEYBOARD = const(0x2)
    ELASTOMER = const(0x3)
    ELASTOMER_LEDPIXEL = const(0x4)


JD_MATRIX_KEYPAD_REG_PRESSED = const(JD_REG_READING)
JD_MATRIX_KEYPAD_REG_ROWS = const(0x180)
JD_MATRIX_KEYPAD_REG_COLUMNS = const(0x181)
JD_MATRIX_KEYPAD_REG_LABELS = const(0x182)
JD_MATRIX_KEYPAD_REG_VARIANT = const(JD_REG_VARIANT)
JD_MATRIX_KEYPAD_EV_DOWN = const(JD_EV_ACTIVE)
JD_MATRIX_KEYPAD_EV_UP = const(JD_EV_INACTIVE)
JD_MATRIX_KEYPAD_EV_CLICK = const(0x80)
JD_MATRIX_KEYPAD_EV_LONG_CLICK = const(0x81)
JD_MATRIX_KEYPAD_PACK_FORMATS = {
    JD_MATRIX_KEYPAD_REG_PRESSED: "r: u8",
    JD_MATRIX_KEYPAD_REG_ROWS: "u8",
    JD_MATRIX_KEYPAD_REG_COLUMNS: "u8",
    JD_MATRIX_KEYPAD_REG_LABELS: "r: z",
    JD_MATRIX_KEYPAD_REG_VARIANT: "u8",
    JD_MATRIX_KEYPAD_EV_DOWN: "u8",
    JD_MATRIX_KEYPAD_EV_UP: "u8",
    JD_MATRIX_KEYPAD_EV_CLICK: "u8",
    JD_MATRIX_KEYPAD_EV_LONG_CLICK: "u8"
}
