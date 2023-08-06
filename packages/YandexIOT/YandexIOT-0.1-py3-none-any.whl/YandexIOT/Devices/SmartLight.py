import colorsys
from YandexIOT.Devices import SmartDevice
from YandexIOT.Devices.SmartDevice import UnsupportedFeature


class SmartLight(SmartDevice):
    def __init__(self, device_json, home):
        super(SmartLight, self).__init__(device_json, home)

    def turn_on(self):
        """Turn on the light.

        :return: SmartDeviceResponse
        """

        return self._change_state(True)

    def turn_off(self):
        """Turn off the light.

        :return: SmartDeviceResponse
        """

        return self._change_state(False)

    def set_brightness(self, value):
        """Change the brightness level of the light.

        :param value: A value from 1 to 100.
        :return: SmartDeviceResponse
        """

        return self._change_brightness(value)

    def set_color(self, color):
        """Change the color of the light.

        :param color: A tuple of 3 RGB integers.
        :return: SmartDeviceResponse
        """

        return self._change_color(color)

    def set_scene(self, scene):
        """Change the scene of the light.

        :param scene: Scene type.
        :return: SmartDeviceResponse
        """

        return self._change_scene(scene)

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

    def _change_brightness(self, value):
        if "devices.capabilities.range" not in self.get_capabilities():
            raise UnsupportedFeature(f"Device '{self.get_name()}' does not support changing its brightness.")

        return self._send_actions([
            {
                "type": "devices.capabilities.range",
                "state": {
                    "instance": "brightness",
                    "value": value
                }
            }
        ])

    def _change_color(self, color):
        if "devices.capabilities.color_setting" not in self.get_capabilities():
            raise UnsupportedFeature(f"Device '{self.get_name()}' does not support changing its color.")

        value = None
        color_model = self.get_device_color_model()

        if color_model == "rgb":
            value = int('%02x%02x%02x' % color, 16)
        elif color_model == "hsv":
            (h, s, v) = colorsys.rgb_to_hsv(color[0] / 255, color[1] / 255, color[2] / 255)
            value = {
                "h": int(h * 360),
                "s": int(s * 100),
                "v": int(v * 100),
            }

        return self._send_actions([
            {
                "type": "devices.capabilities.color_setting",
                "state": {
                    "instance": color_model,
                    "value": value
                }
            }
        ])

    def _change_scene(self, scene):
        if "devices.capabilities.color_setting" not in self.get_capabilities():
            raise UnsupportedFeature(f"Device '{self.get_name()}' does not support changing its scene.")

        if scene not in self.get_scenes():
            raise InvalidLightScene(f"Invalid scene '{scene}' for '{self.get_name()}'. "
                                    f"Try to call SmartLight.get_scenes() to get available scenes.")

        return self._send_actions([
            {
                "type": "devices.capabilities.color_setting",
                "state": {
                    "instance": "scene",
                    "value": scene
                }
            }
        ])

    def get_device_color_model(self):
        model = "rgb"
        for i in self._device_json()["capabilities"]:
            if i['type'] == "devices.capabilities.color_setting":
                model = i['parameters']['color_model']
                break
        return model

    def get_scenes(self):
        for i in self._device_json()["capabilities"]:
            if 'color_scene' in i['parameters']:
                return [j['id'] for j in i['parameters']['color_scene']['scenes']]

        return []


class InvalidLightScene(Exception):
    pass
