from YandexIOT.Devices import SmartDevice
from YandexIOT.Devices.SmartDevice import UnsupportedFeature


class SmartVacuum(SmartDevice):
    def __init__(self, device_json, home):
        super(SmartVacuum, self).__init__(device_json, home)

    def turn_on(self):
        """Turn on the vacuum.

        :return: SmartDeviceResponse
        """

        return self._change_state(True)

    def _change_state(self, state):
        if "devices.capabilities.on_off" not in self.get_capabilities():
            raise UnsupportedFeature(f"Device '{self.get_name()}' does not support turning it on/off.")

        return self._send_actions([
            {
                "type": "devices.capabilities.on_off",
                "state": {
                    "instance": "on",
                    "value": state
                }
            }
        ])
