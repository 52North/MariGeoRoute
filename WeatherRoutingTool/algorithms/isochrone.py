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
import numpy as np
from geovectorslib import geod  #TODO: change to geopy?

from algorithms.isobased import IsoBased
from routeparams import RouteParams

class IsoChrone(IsoBased):
    delta_time : int

    def __init__(self, start, finish, time, delta_time):
        IsoBased.__init__(self, start, finish, time)
        self.delta_time = delta_time

    def check_isochrones(self, route : RouteParams):
        debug=False
        if(debug) : print('Checking route for equal time intervals')

        route.print_route()
        for step in range(1,route.count):
            lat1=np.array([float(route.lats_per_step[step-1])])
            lat2=np.array([float(route.lats_per_step[step])])
            lon1=np.array([float(route.lons_per_step[step-1])])
            lon2=np.array([float(route.lons_per_step[step])])
            dist = geod.inverse(lat1, lon1, lat2, lon2)
            time = round(dist['s12'][0]/route.speed_per_step[step])

            if(debug):
                print('Step', step)
                print('lat1 ' + str(lat1) + ' lat2=' + str(lon1) + ' lat2=' + str(lat2) + 'lon2=' + str(lon2))
                print('speed=', route.speed_per_step[step])
                print('dist=', dist['s12'])
                print('time for step ' + str(step) + ' = ' + str(time))

            if not (time==3600):
                exc = 'Timestep ' + str(step) + ' of min.-time route are not equal to ' + str(3600) + ' but ' + str(time)
                raise ValueError(exc)

    def get_dist(self, bs):
        dist = self.delta_time * bs
        print('dist=', dist)
        print('delta_time=', self.delta_time)
        print('bs=', bs)
        return dist

    def get_delta_variables(self, boat, wind, bs):
        dist = self.get_dist(bs)
        delta_fuel = boat.get_fuel_per_time(self.get_current_azimuth(), wind) * self.delta_time

        return self.delta_time, delta_fuel, dist


