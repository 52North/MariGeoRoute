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

import config
from algorithms.isofuel import IsoFuel

class RoutingAlgFactory():

    def __init__(self):
        pass

    def get_routing_alg(self, alg_type):
        ra = None

        r_la1, r_lo1, r_la2, r_lo2 = config.DEFAULT_ROUTE
        start = (r_la1, r_lo1)
        finish = (r_la2, r_lo2)
        start_time = dt.datetime.strptime(config.START_TIME, '%Y%m%d%H')
        delta_fuel = config.DELTA_FUEL
        fig_path = config.FIGURE_PATH
        routing_steps = config.ROUTING_STEPS

        if alg_type=='ISOFUEL':
            ra = IsoFuel(start, finish, start_time, delta_fuel, fig_path)
            ra.set_steps(routing_steps)
            ra.set_pruning_settings(config.ISOCHRONE_PRUNE_SECTOR_DEG_HALF, config.ISOCHRONE_PRUNE_SEGMENTS)
            ra.set_variant_segments(config.ROUTER_HDGS_SEGMENTS, config.ROUTER_HDGS_INCREMENTS_DEG)

        return ra
