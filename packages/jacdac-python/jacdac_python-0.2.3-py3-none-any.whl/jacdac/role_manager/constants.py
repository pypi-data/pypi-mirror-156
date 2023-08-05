# Autogenerated constants for Role Manager service
from jacdac.constants import *
from jacdac.system.constants import *
JD_SERVICE_CLASS_ROLE_MANAGER = const(0x1e4b7e66)
JD_ROLE_MANAGER_REG_AUTO_BIND = const(0x80)
JD_ROLE_MANAGER_REG_ALL_ROLES_ALLOCATED = const(0x181)
JD_ROLE_MANAGER_CMD_SET_ROLE = const(0x81)
JD_ROLE_MANAGER_CMD_CLEAR_ALL_ROLES = const(0x84)
JD_ROLE_MANAGER_CMD_LIST_ROLES = const(0x83)
JD_ROLE_MANAGER_EV_CHANGE = const(JD_EV_CHANGE)
JD_ROLE_MANAGER_PACK_FORMATS = {
    JD_ROLE_MANAGER_REG_AUTO_BIND: "u8",
    JD_ROLE_MANAGER_REG_ALL_ROLES_ALLOCATED: "u8",
    JD_ROLE_MANAGER_CMD_SET_ROLE: "b[8] u8 s",
    JD_ROLE_MANAGER_CMD_LIST_ROLES: "b[12]"
}
