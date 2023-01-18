import numpy as np
import datetime as dt
from global_land_mask import globe
import cartopy.crs as ccrs
import cartopy.feature as cf

import utils as ut
import xarray as xr
import matplotlib.pyplot as plt
import routeparams
from weather import WeatherCond
from graphics import *


class Constraint():
    name: str
    message: str
    lat: np.ndarray
    lon: np.ndarray
    time: np.ndarray
    resource_type: int

    def __init__(self, name):
        self.name = name

    def get_resource_type(self):
        return self.resource_type

    def print_constraint_message(self):
        print(self.message)
        pass

    def constraint_on_point(self, lat, lon, time):
        pass

    def print_debug(self, message):
        print(self.name + str(': ') + str(message))

    def print_info(self):
        pass

    def plot_route_in_constraint(self):
        pass

class PositiveConstraint(Constraint):
    def __init__(self, name):
        Constraint.__init__(self, name)


class NegativeContraint(Constraint):
    def __init__(self, name):
        Constraint.__init__(self, name)
        self.message = 'At least one point discarded as '


class NegativeConstraintFromWeather(NegativeContraint):
    wt: WeatherCond

    def __init__(self, name, weather):
        NegativeContraint.__init__(self, name)
        self.wt = weather

    def check_weather(self, lat, lon, time):
        pass


class ConstraintPars():
    resolution: int
    bCheckEndPoints: bool
    bCheckCrossing: bool

    def __init__(self):
        self.resolution = 1. / 10
        self.bCheckEndPoints = True
        self.bCheckCrossing = True

    def print(self):
        print('Print settings of Constraint Pars:')
        ut.print_step('resolution=' + str(self.resolution))
        ut.print_step('bCheckEndPoints=' + str(self.bCheckEndPoints))


class ConstraintsList():
    pars: ConstraintPars
    positive_constraints: list
    negative_constraints: list
    constraints_crossed: list
    weather: WeatherCond
    neg_size: int
    pos_size: int

    def __init__(self, pars):
        self.pars = pars
        self.positive_constraints = []
        self.negative_constraints = []
        self.constraints_crossed = []
        self.neg_size = 0
        self.pos_size = 0

    def print_constraints_crossed(self):
        print('Discarding point as:')
        for iConst in range(0, len(self.constraints_crossed)):
            ut.print_step(str(self.constraints_crossed[iConst]), 1)

    def print_settings(self):
        self.pars.print()
        self.print_active_constraints()

    def print_active_constraints(self):
        for Const in self.negative_constraints:
            Const.print_info()

        for Const in self.positive_constraints:
            Const.print_info()

    def shall_I_pass(self, lat, lon, time):
        is_constrained = [False for i in range(0, lat.shape[1])]

        if self.pars.bCheckCrossing:
            is_constrained = self.safe_crossing(lat, lon, time)
        elif self.pars.bCheckEndPoints:
            is_constrained = self.safe_endpoint(lat, lon, time, is_constrained)
        if is_constrained.any(): self.print_constraints_crossed()

    def split_route(self):
        pass

    def safe_endpoint(self, lat, lon, time, is_constrained):
        debug = False

        for iConst in range(0, self.neg_size):
            is_constrained_temp = self.negative_constraints[iConst].constraint_on_point(lat, lon, time)
            if is_constrained_temp.any(): self.constraints_crossed.append(self.negative_constraints[iConst].message)
            if (debug):
                print('is_constrained_temp: ', is_constrained_temp)
                print('is_constrained: ', is_constrained)
            is_constrained += is_constrained_temp
        # if (is_constrained.any()) & (debug): self.print_constraints_crossed()
        return is_constrained

    def safe_crossing(self, lat_start, lat_end, lon_start, lon_end, time, is_constrained):
        debug = True

        delta_lats = (lat_end - lat_start) * self.pars.resolution
        delta_lons = (lon_end - lon_start) * self.pars.resolution
        x0 = lat_start
        y0 = lon_start

        # if (debug):
        # ut.print_step('Constraints: Moving from (' + str(lat_start) + ',' + str(lon_start) + ') to (' + str(
        #        lat_end) + ',' + str(lon_end), 0)

        nSteps = int(1. / self.pars.resolution)
        for iStep in range(0, nSteps):
            x = x0 + delta_lats
            y = y0 + delta_lons

            is_constrained = self.safe_endpoint(x, y, time, is_constrained)
            x0 = x
            y0 = y

        if (debug):
            lat_start_constrained = lat_start[is_constrained == 1]
            lon_start_constrained = lon_start[is_constrained == 1]
            lat_end_constrained = lat_end[is_constrained == 1]
            lon_end_constrained = lon_end[is_constrained == 1]

            if lat_start_constrained.shape[0] > 0: ut.print_step('transitions constrained:', 1)
            for i in range(0, lat_start_constrained.shape[0]):
                ut.print_step('[' + str(lat_start_constrained[i]) + ',' + str(lon_start_constrained[i]) + '] to [' +
                              str(lat_end_constrained[i]) + ',' + str(lon_end_constrained[i]) + ']', 2)

        # if not ((round(x0.all,8) == round(self.lats_per_step[0, :].all) and (x0.all == self.lons_per_step[0, :].all)):
        #    exc = 'Did not check destination, only checked lat=' + str(x0) + ', lon=' + str(y0)
        #    raise ValueError(exc)

        if not np.allclose(x, lat_end): raise Exception(
            'Constraints.land_crossing(): did not reach latitude of destination!')
        if not np.allclose(y, lon_end): raise Exception(
            'Constraints.land_crossing(): did not reach longitude of destination!')

        return is_constrained

    def add_pos_constraint(self, constraint):
        self.positive_constraints.append(constraint)
        self.pos_size += 1

    def add_neg_constraint(self, constraint):
        self.negative_constraints.append(constraint)
        self.neg_size += 1

    def check_weather(self):
        pass


class LandCrossing(NegativeContraint):

    def __init__(self):
        NegativeContraint.__init__(self, 'LandCrossing')
        self.message += 'crossing land!'
        self.resource_type = 0

    def constraint_on_point(self, lat, lon, time):
        # self.print_debug('checking point: ' + str(lat) + ',' + str(lon))
        return globe.is_land(lat, lon)

    def print_info(self):
        ut.print_step('no land crossing')


class WaveHeight(NegativeConstraintFromWeather):
    current_wave_height: np.ndarray
    max_wave_height: float

    def __init__(self):
        NegativeContraint.__init__(self, 'WaveHeight')
        self.message += 'waves are to high!'
        self.resource_type = 0
        self.current_wave_height = np.array([-99])
        self.max_wave_height = 10

    def constraint_on_point(self, lat, lon, time):
        # self.print_debug('checking point: ' + str(lat) + ',' + str(lon))
        self.check_weather(lat, lon, time)
        # print('current_wave_height:', self.current_wave_height)
        return self.current_wave_height > self.max_wave_height

    def print_info(self):
        ut.print_step('maximum wave height=' + str(self.max_wave_height) + 'm')


class WaterDepth(NegativeConstraintFromWeather):
    current_depth: np.ndarray
    min_depth: float

    def __init__(self, weather):
        NegativeConstraintFromWeather.__init__(self, 'WaterDepth', weather)
        self.message += 'water not deep enough!'
        self.resource_type = 0
        self.current_depth = np.array([-99])
        self.min_depth = 50

    def set_drought(self, depth):
        self.min_depth = depth

    def constraint_on_point(self, lat, lon, time):
        self.check_weather(lat, lon, time)
        returnvalue = self.current_depth > -self.min_depth
        # ut.print_step('current_depth:' + str(self.current_depth), 1)
        return returnvalue

    def check_weather(self, lat, lon, time):
        self.current_depth = np.full(lat.shape, -99)

        for i in range(0, lat.shape[0]):
            self.current_depth[i] = self.get_current_depth(lat[i], lon[i])

    def print_info(self):
        ut.print_step('minimum water depth=' + str(self.min_depth) + 'm')

    def get_current_depth(self, lat, lon):
        rounded_ds = self.wt.ds['depth'].interp(latitude=lat, longitude=lon, method='linear')
        if np.isnan(rounded_ds):
            raise Exception('Constraints: depth is nan!')
        return rounded_ds

    def plot_depth_map_from_file(self, path, lat_start, lon_start, lat_end, lon_end):
        level_diff = 10

        ds_depth = xr.open_dataset(path)
        depth = ds_depth['z'].where(
            (ds_depth.lat > lat_start) & (ds_depth.lat < lat_end) & (ds_depth.lon > lon_start) & (
                        ds_depth.lon < lon_end) & (ds_depth.z < 0), drop=True)

        # depth = ds_depth['deptho'].where((ds_depth.latitude > lat_start) & (ds_depth.latitude < lat_end) & (ds_depth.longitude > lon_start) & (ds_depth.longitude < lon_end),drop=True) #.where((ds_depth.deptho>-100) & (ds_depth.deptho<0) )

        fig, ax = plt.subplots(figsize=(12, 10))
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        depth.plot.contourf(ax=ax,
                            # extend='max',
                            # levels=np.arange(-60, 0, 0.1),  high-resolution contours
                            levels=np.arange(-100, 0, level_diff),
                            transform=ccrs.PlateCarree())

        fig.subplots_adjust(
            left=0.05,
            right=1,
            bottom=0.05,
            top=0.95,
            wspace=0,
            hspace=0)
        ax.add_feature(cf.LAND)
        ax.add_feature(cf.COASTLINE)
        ax.gridlines(draw_labels=True)

        plt.show()

    def plot_route_in_constraint(self, route: RouteParams, colour, figure_file):
        level_diff = 10

        depth = self.wt.ds['depth'].where((self.wt.ds.depth < 0), drop=True)

        fig, ax = plt.subplots(figsize=(12, 10))
        ax.axis('off')
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        depth.plot.contourf(ax=ax,
                            levels=np.arange(-100, 0, level_diff),
                            transform=ccrs.PlateCarree())

        fig.subplots_adjust(
            left=0.05,
            right=0.95,
            bottom=0.05,
            top=0.95,
            wspace=0,
            hspace=0)
        ax.add_feature(cf.LAND)
        ax.add_feature(cf.COASTLINE)
        ax.gridlines(draw_labels=True)

        lats = route.lats_per_step
        lons = route.lons_per_step
        time = route.time
        ax.plot(lons, lats, 'r-')

        plt.title('Route British Channel - ' + str(self.min_depth) + 'm drought')

        plt.savefig(figure_file + '/route_waterdepth.png')
