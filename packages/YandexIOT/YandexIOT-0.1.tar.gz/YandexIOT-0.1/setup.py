from setuptools import find_packages, setup

setup(name='YandexIOT',
      version='0.1',
      description='Library for controlling Yandex Smart Devices in Python',
      url='https://github.com/Artingl/YandexIOT',
      author='Artingl',
      author_email='mikrobamboni@yandex.ru',
      packages=['YandexIOT', 'YandexIOT.Devices'],
      install_requires=[
          'requests==2.27.1',
      ])
