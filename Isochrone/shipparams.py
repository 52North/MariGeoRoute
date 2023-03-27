import numpy as np
import datetime as dt
from typing import NamedTuple
import json
import dateutil.parser

import utils
import matplotlib.pyplot as plt
import graphics
from utils import NumpyArrayEncoder


class ShipParams():
    fuel: tuple
    power: tuple
    rpm: tuple
    speed: tuple
    fuel_type: str

    def __init__(self, fuel, power, rpm,):
        self.fuel = fuel
        self.power = power
        self.rpm = rpm
        self.speed = -99
        self.fuel_type = 'HFO'

    def set_default(self):
        self.fuel = -99
        self.power = -99
        self.rpm = -99
        self.speed = -99
        self.fuel_type = -99

    def print(self):
        print('fuel = ', self.fuel)
        print('rpm = ', self.rpm)
        print('power = ', self.power)
        print('speed = ', self.speed)
        print('fuel_type = ', self.fuel_type)

    def get_power(self):
        return self.power

    def get_fuel(self):
        return self.fuel

    def get_fuel_type(self):
        return self.fuel_type

    def get_rpm(self):
        return self.rpm

    def get_speed(self):
        return self.speed