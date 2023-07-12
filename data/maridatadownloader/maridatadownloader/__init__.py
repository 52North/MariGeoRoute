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
from maridatadownloader.opendap import DownloaderOpendapCMEMS, DownloaderOpendapGFS


class DownloaderFactory:
    def __init__(self):
        pass

    @classmethod
    def get_downloader(cls, downloader_type, platform, username=None, password=None, **kwargs):
        if downloader_type.lower() == 'opendap':
            if platform.lower() == 'gfs':
                return DownloaderOpendapGFS(username=username, password=password)
            elif platform.lower() == 'cmems':
                assert 'product' in kwargs, "kwargs['product'] is required for platform=cmems"
                assert 'product_type' in kwargs, "kwargs['product_type'] is required for platform=cmems"
                assert username, "username is required for platform=cmems"
                assert password, "password is required for platform=cmems"
                return DownloaderOpendapCMEMS(kwargs['product'], kwargs['product_type'], username, password)
            else:
                raise ValueError(platform)
        else:
            raise ValueError(downloader_type)
