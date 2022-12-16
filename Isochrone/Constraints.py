import numpy as np
import datetime as dt
from global_land_mask import globe

import utils as ut
from weather import WeatherCond

class Constraint():
    name : str
    message : str
    lat : np.ndarray
    lon : np.ndarray
    time : np.ndarray
    resource_type : int

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


class PositiveConstraint(Constraint):
    def __init__(self,name):
        Constraint.__init__(self,name)

class NegativeContraint(Constraint):
    def __init__(self, name):
        Constraint.__init__(self, name)
        self.message = 'At least one point discarded as '

class ConstraintPars():
    resolution : int
    bCheckEndPoints : bool
    bCheckCrossing : bool
    bConsiderLand : bool
    def __init__(self):
        self.resolution = 1./10
        self.bCheckEndPoints = True
        self.bCheckCrossing = True
        self.bConsiderLand = True

    def print(self):
        print('Print settings of Constraint Pars:')
        ut.print_step('resolution=' + str(self.resolution))
        ut.print_step('bCheckEndPoints=' + str(self.bCheckEndPoints))
        ut.print_step('bCheckCrossing=' + str(self.bCheckCrossing))
        ut.print_step('bConsiderLand=' + str(self.bConsiderLand))

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
        for iConst in range(0,len(self.constraints_crossed)):
            ut.print_step(str(self.constraints_crossed[iConst]),1)
    def print_settings(self):
        self.pars.print()
    def shall_I_pass(self, lat, lon, time):
        is_constrained = [False for i in range(0, lat.shape[1])]

        if self.pars.bCheckEndPoints: is_constrained=self.safe_endpoint(lat, lon, time, is_constrained)
        if self.pars.bCheckCrossing: is_constrained=self.safe_crossing(lat,lon,time)

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
        if (is_constrained.any()) & (debug): self.print_constraints_crossed()
        return is_constrained

    def safe_crossing(self, lat_start, lat_end, lon_start, lon_end, time, is_constrained):
        debug = False

        delta_lats = (lat_end - lat_start) * self.pars.resolution
        delta_lons = (lon_end - lon_start) * self.pars.resolution
        x0 = lat_start
        y0 = lon_start
        if debug: print('lats_per_step shape', lat_start.shape[0])

        if (debug):
            print(
                'Moving from (' + str(lat_start) + ',' + str(lon_start) + ') to (' + str(
                    lat_end) + ',' + str(lon_end))
            print('x0=' + str(x0) + ', y0=' + str(y0))
            print('is_on_land', is_constrained)
            print('delta_lats', delta_lats)
            print('delta_lons', delta_lons)

        nSteps = int(1. / self.pars.resolution)
        for iStep in range(0, nSteps):
            x = x0 + delta_lats
            y = y0 + delta_lons
            if (debug):
                print('     iStep=', iStep)
                print('     x=', x)
                print('     y=', y)

            is_constrained = self.safe_endpoint(x, y, time, is_constrained)
            if debug: print('is_constrained', is_constrained)
            x0 = x
            y0 = y

        # if not ((round(x0.all,8) == round(self.lats_per_step[0, :].all) and (x0.all == self.lons_per_step[0, :].all)):
        #    exc = 'Did not check destination, only checked lat=' + str(x0) + ', lon=' + str(y0)
        #    raise ValueError(exc)

        if not np.allclose(x,lat_end): raise Exception('Constraints.land_crossing(): did not reach latitude of destination!')
        if not np.allclose(y,lon_end): raise Exception('Constraints.land_crossing(): did not reach longitude of destination!')

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
        NegativeContraint.__init__(self,'LandCrossing')
        self.message += 'crossing land!'
        self.resource_type = 0

    def constraint_on_point(self, lat, lon, time):
        #self.print_debug('checking point: ' + str(lat) + ',' + str(lon))
        return globe.is_land(lat, lon)

class WaveHeight(NegativeContraint):
    current_wave_height : np.ndarray
    max_wave_height: float

    def __init__(self):
        NegativeContraint.__init__(self,'WaveHeight')
        self.message += 'waves are to high!'
        self.resource_type = 0
        self.current_wave_height = np.array([-99])
        self.max_wave_height = 10

    def constraint_on_point(self, lat, lon, time):
        #self.print_debug('checking point: ' + str(lat) + ',' + str(lon))
        self.check_weather(lat, lon, time)
        #print('current_wave_height:', self.current_wave_height)
        return self.current_wave_height > self.max_wave_height

    def check_weather(self, lat, lon, time):
        #self.print_debug('checking weather')
        pass
