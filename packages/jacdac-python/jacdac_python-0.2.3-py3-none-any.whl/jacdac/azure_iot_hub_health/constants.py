# Autogenerated constants for Azure IoT Hub Health service
from enum import IntEnum
from jacdac.constants import *
from jacdac.system.constants import *
JD_SERVICE_CLASS_AZURE_IOT_HUB_HEALTH = const(0x1462eefc)


class AzureIotHubHealthConnectionStatus(IntEnum):
    CONNECTED = const(0x1)
    DISCONNECTED = const(0x2)
    CONNECTING = const(0x3)
    DISCONNECTING = const(0x4)


JD_AZURE_IOT_HUB_HEALTH_REG_HUB_NAME = const(0x180)
JD_AZURE_IOT_HUB_HEALTH_REG_HUB_DEVICE_ID = const(0x181)
JD_AZURE_IOT_HUB_HEALTH_REG_CONNECTION_STATUS = const(0x182)
JD_AZURE_IOT_HUB_HEALTH_REG_PUSH_PERIOD = const(0x80)
JD_AZURE_IOT_HUB_HEALTH_REG_PUSH_WATCHDOG_PERIOD = const(0x81)
JD_AZURE_IOT_HUB_HEALTH_CMD_CONNECT = const(0x81)
JD_AZURE_IOT_HUB_HEALTH_CMD_DISCONNECT = const(0x82)
JD_AZURE_IOT_HUB_HEALTH_CMD_SET_CONNECTION_STRING = const(0x86)
JD_AZURE_IOT_HUB_HEALTH_EV_CONNECTION_STATUS_CHANGE = const(JD_EV_CHANGE)
JD_AZURE_IOT_HUB_HEALTH_EV_MESSAGE_SENT = const(0x80)
JD_AZURE_IOT_HUB_HEALTH_PACK_FORMATS = {
    JD_AZURE_IOT_HUB_HEALTH_REG_HUB_NAME: "s",
    JD_AZURE_IOT_HUB_HEALTH_REG_HUB_DEVICE_ID: "s",
    JD_AZURE_IOT_HUB_HEALTH_REG_CONNECTION_STATUS: "u16",
    JD_AZURE_IOT_HUB_HEALTH_REG_PUSH_PERIOD: "u32",
    JD_AZURE_IOT_HUB_HEALTH_REG_PUSH_WATCHDOG_PERIOD: "u32",
    JD_AZURE_IOT_HUB_HEALTH_CMD_SET_CONNECTION_STRING: "s",
    JD_AZURE_IOT_HUB_HEALTH_EV_CONNECTION_STATUS_CHANGE: "u16"
}
