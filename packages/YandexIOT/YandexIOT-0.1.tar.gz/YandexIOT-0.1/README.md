# YandexIOT
Library for controlling Yandex Smart Devices in Python.

## Install

```shell
pip install YandexIOT
```

## Devices
Currently, it supports only controlling light, but other devices are going to be implemented soon.

## Example

```python
from YandexIOT import SmartHome

home = SmartHome("YOUR_TOKEN_HERE")

light = home.get_device_by_name("Лампочка")
light.turn_on()

```
