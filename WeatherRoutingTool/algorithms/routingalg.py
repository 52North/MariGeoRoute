#   Copyright (C) 2021 - 2023 52°North Spatial Information Research GmbH
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# If the program is linked with libraries which are licensed under one of
# the following licenses, the combination of the program with the linked
# library is not considered a "derivative work" of the program:
#
#     - Apache License, version 2.0
#     - Apache Software License, version 1.0
#     - GNU Lesser General Public License, version 3
#     - Mozilla Public License, versions 1.0, 1.1 and 2.0
#     - Common Development and Distribution License (CDDL), version 1.0
#
# Therefore the distribution of the program linked with libraries licensed
# under the aforementioned licenses, is permitted by the copyright holders
# if the distribution is compliant with both the GNU General Public
# License version 2 and the aforementioned licenses.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
import datetime as dt
import logging
import time

import numpy as np
import matplotlib
from geovectorslib import geod
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import utils.formatting as form
from constraints.constraints import *
from ship.ship import Boat
from routeparams import RouteParams
from weather import WeatherCond

logger = logging.getLogger('WRT.routingalg')

class RoutingAlg():
    """
        Isochrone data structure with typing.
                Parameters:
                    count: int  (routing step)
                    start: tuple    (lat,long at start)
                    finish: tuple   (lat,lon and end)
                    gcr_azi: float (initial gcr heading)
                    lats1, lons1, azi1, s12: (M, N) arrays, N=headings+1, M=number of steps+1 (decreasing step number)
                    azi0, s0: (M, 1) vectors without history
                    time1: current datetime
                    elapsed: complete elapsed timedelta
        """
    ncount: int  # total number of routing steps
    count: int  # current routing step

    start: tuple  # lat, lon at start
    finish: tuple  # lat, lon at end
    departure_time: dt.datetime
    gcr_azi: float  # azimut of great circle route

    fig: matplotlib.figure
    route_ensemble : list
    figure_path : str

    def __init__(self, start, finish, departure_time, figure_path=""):
        self.count = 0
        self.start = start
        self.finish = finish
        self.departure_time = departure_time

        gcr = self.calculate_gcr(start, finish)
        self.current_azimuth = gcr
        self.gcr_azi = gcr

        self.figure_path = figure_path

        self.print_init()

    def init_fig(self):
        pass

    def update_fig(self):
        pass

    def print_init(self):
        logger.info('Initialising routing:')
        logger.info(form.get_log_step('route from ' + str(self.start) + ' to ' + str(self.finish),1))
        logger.info(form.get_log_step('start time ' + str(self.departure_time),1))

    def print_current_status(self):
        pass

    def set_steps(self, steps):
        self.ncount = steps

    def calculate_gcr(self, start, finish):
        gcr = geod.inverse([start[0]], [start[1]], [finish[0]], [
            finish[1]])  # calculate distance between start and end according to Vincents approach, return dictionary
        return gcr['azi1']

    def execute_routing(self, boat: Boat, wt : WeatherCond, constraints_list : ConstraintsList, verbose=False):
        pass

    def check_for_positive_constraints(self, constraint_list):
        pass

    def terminate(self):
        form.print_line()
        print('Terminating...')

        self.check_destination()
        self.check_positive_power()
        pass

    def check_destination(self):
        pass

    def check_positive_power(self):
        pass

