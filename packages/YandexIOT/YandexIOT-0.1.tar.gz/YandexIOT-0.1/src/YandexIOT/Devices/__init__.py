from .SmartDevice import SmartDevice
from .SmartLight import SmartLight
from .SmartVacuum import SmartVacuum


TYPES = {
    "devices.types.light": SmartLight,
    "devices.types.vacuum_cleaner": SmartVacuum,
}
