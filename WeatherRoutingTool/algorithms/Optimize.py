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
from pymoo.factory import get_termination
from pymoo.optimize import minimize
from pymoo.operators.crossover.sbx import SBX

pop_size = 2
n_gen = 2
n_offspring = 4
#cost[nan_mask] = 20000000000* np.nanmax(cost) if np.nanmax(cost) else 0
problem = RoutingProblem()
algorithm = NSGA2(pop_size=pop_size,
                  sampling= Population(start, end, cost),
                  crossover= Crossover1(),
                  n_offsprings = 2,
                  mutation= Mutation1(),
                  eliminate_duplicates=False)
termination = get_termination("n_gen", n_gen)

res = minimize(problem,
               algorithm,
               termination,
               save_history=True, 
               verbose=True)
#stop = timeit.default_timer()
#route_cost(res.X)