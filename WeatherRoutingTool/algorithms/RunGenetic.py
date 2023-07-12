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
from DataUtils import *
from Genetic import *
from GeneticUtils import *

path = '/home/parichay/MariGeoRoute/Genetic/Data/CMEMS/'
data = loadData(path)
lon_min, lon_max, lat_min, lat_max = getBBox(-80, 32,-5, 47, data)
wave_height = data.isel(longitude=slice(lon_min, lon_max), latitude=slice(lat_min, lat_max))
cost = cleanData(wave_height.data)
start, end = findStartAndEnd(40.7128,-74.0060,38.7223,-9.1393, wave_height)
#GeneticUtils.data = wave_height
set_data(wave_height, cost)
res = optimize(start, end, cost)

# get the best solution
best_idx = res.F.argmin()
best_x = res.X[best_idx]
best_f = res.F[best_idx]
route=best_x[0]

print(route)