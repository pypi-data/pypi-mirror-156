import requests


class SmartDeviceResponse:
    def __init__(self, response_json):
        self.__response_json = response_json

    def get_status_str(self):
        return self.__response_json['status']

    def get_status(self):
        return self.__response_json['status'] == "ok"

    def get_message(self):
        return "" if "message" not in self.__response_json else self.__response_json['message']


class SmartDevice:
    def __init__(self, device_json, home):
        self.__device_json = device_json
        self.__home = home

        self._capabilities = []

        for i in self.__device_json['capabilities']:
            self._capabilities.append(i['type'])

    def _get_home(self):
        return self.__home

    def _device_json(self):
        return self.__device_json

    def _send_actions(self, actions: list):
        req = requests.post("https://api.iot.yandex.net/v1.0/devices/actions",
                            headers=self._get_home().headers,
                            json={
                                "devices": [{
                                    "id": self.get_id(),
                                    "actions": actions
                                }]
                            })
        return SmartDeviceResponse(req.json())

    def get_capabilities(self):
        return self._capabilities

    def get_id(self):
        return self.__device_json['id']

    def get_name(self):
        return self.__device_json['name']

    def get_type(self):
        return self.__device_json['type']


class UnsupportedFeature(Exception):
    pass
