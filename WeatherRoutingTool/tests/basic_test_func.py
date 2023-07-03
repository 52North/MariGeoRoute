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
import datetime
import os

import xarray
import pytest

from algorithms.isobased import IsoBased
from algorithms.isofuel import IsoFuel
from constraints.constraints import *

def generate_dummy_constraint_list():
    pars = ConstraintPars()
    pars.resolution = 1./10

    constraint_list = ConstraintsList(pars)
    return constraint_list

def create_dummy_IsoBased_object():
    start = (30, 45)
    finish = (0, 20)
    date = datetime.date.today()
    prune_sector_half = 90
    nof_prune_segments = 5
    nof_hdgs_segments = 4
    hdgs_increments = 1

    ra = IsoBased(start, finish, date)
    ra.set_pruning_settings(prune_sector_half, nof_prune_segments)
    ra.set_variant_segments(nof_hdgs_segments, hdgs_increments)
    return ra

def create_dummy_IsoFuel_object():
    start = (30, 45)
    finish = (0, 20)
    date = datetime.date.today()
    prune_sector_half = 90
    nof_prune_segments = 5
    nof_hdgs_segments = 4
    hdgs_increments = 1

    ra = IsoFuel(start, finish, date, 999, "")
    ra.set_pruning_settings(prune_sector_half, nof_prune_segments)
    ra.set_variant_segments(nof_hdgs_segments, hdgs_increments)
    return ra
