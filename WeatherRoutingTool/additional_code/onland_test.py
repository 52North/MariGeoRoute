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
from global_land_mask import globe
c=0
v=0
w=0
for i in range(int((62.3 - 59.5) / 0.0003) + 1):
    c=c+1
    try:
        x = 59.5 + i * 0.0003
        y = (24.6 - 17.6) / (59.5 - 62.3) * (x - 59.5) + 17.6
        print(x,y)
    except:
        continue
    is_on_land = globe.is_land(float(x), float(y))
    if not is_on_land:
        # print("in water")
        w=w+1
    if is_on_land:
        #print("crosses land")
        v=v+1
print("for loop run",c)
print("crosses land",v)
print("in water",w)
#print(crosses_land(62.3, 17.6, 59.5,24.6))
#crosses_land(59.5, 17.6, 62.3,24.6)
#
# for i in range(int((5 - 4) / 0.0003) + 1):
#     print(i)
#     print("hello")