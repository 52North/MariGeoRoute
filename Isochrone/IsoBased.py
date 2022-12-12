import numpy as np
import datetime as dt
import utils as ut
from polars import Boat
from typing import NamedTuple
from geovectorslib import geod
from weather import WeatherCond
from global_land_mask import globe
from scipy.stats import binned_statistic
from routeparams import RouteParams
from RoutingAlg import RoutingAlg
import utils

class IsoBased(RoutingAlg):
    def __init__(self, start, finish, time):
        RoutingAlg.__init__(self, start, finish, time)
        self.current_variant=self.current_azimuth

    def check_variant_def(self):
        if (not ((self.lats_per_step.shape[1] == self.lons_per_step.shape[1]) and
                 (self.lats_per_step.shape[1] == self.azimuth_per_step.shape[1]) and
                 (self.lats_per_step.shape[1] == self.dist_per_step.shape[1]))):
            raise 'define_variants: number of columns not matching!'

        if (not ((self.lats_per_step.shape[0] == self.lons_per_step.shape[0]) and
                 (self.lats_per_step.shape[0] == self.azimuth_per_step.shape[0]) and
                 (self.lats_per_step.shape[0] == self.dist_per_step.shape[0]) and
                 (self.lats_per_step.shape[0] == (self.count+1)))):
            raise ValueError(
                'define_variants: number of rows not matching! count = ' + str(self.count) + ' lats per step ' + str(
                    self.lats_per_step.shape[0]))

    def pruning_per_step(self,  trim=True):
        """
              generate view of the iso that only contains the longests route per azimuth segment

              Binned statistic.
              +            iso2 = prune_isochrone(iso2, 'azi02', 's02', bins, True)
              print('iso2 ',iso2)  #

                    Parameters:
                    iso: isochrone dictionary
                    x: values to binarize
                    y: values to apply max to
                    bins: bins edges, dimension is n_bins + 1
                    trim: whether return just one of max values
                    Returns:
                        pruned isochrone dictionary with max values in each bin
                   """
        debug = False
        if(debug): print('Pruning...')

        mean_dist = np.mean(self.full_dist_traveled)
        gcr_point = geod.direct(
            [self.start[0]],
            [self.start[1]],
            self.gcr_azi, mean_dist)

        new_azi = geod.inverse(
            gcr_point['lat2'],
            gcr_point['lon2'],
            [self.finish[0]],
            [self.finish[1]]
        )

        if(debug): print('mean azimuth', new_azi['azi1'])

        azi0s = np.repeat(
            new_azi['azi1'],
            self.prune_segments + 1)

        # determine bins
        delta_hdgs = np.linspace(
            -self.prune_sector_deg_half,
            +self.prune_sector_deg_half,
            self.prune_segments + 1)  # -90,+90,181

        bins = azi0s - delta_hdgs
        bins = np.sort(bins)

        if(debug):
            print('binning for pruning', bins)
            print('current courses', self.current_azimuth)

        idxs = []
        bin_stat, bin_edges, bin_number = binned_statistic(
            self.current_variant, self.full_dist_traveled, statistic=np.nanmax, bins=bins)

        if trim:
            for i in range(len(bin_edges) - 1):
                try:
                    idxs.append(
                        np.where(self.full_dist_traveled == bin_stat[i])[0][0])
                except IndexError:
                    pass
            idxs = list(set(idxs))
        else:
            for i in range(len(bin_edges) - 1):
                idxs.append(np.where(self.full_dist_traveled == bin_stat[i])[0])
            idxs = list(set([item for subl in idxs for item in subl]))

        if(debug):
            print('full_dist_traveled', self.full_dist_traveled)
            print('Indexes that passed', idxs)

        # Return a trimmed isochrone
        self.lats_per_step = self.lats_per_step[:, idxs]
        self.lons_per_step = self.lons_per_step[:, idxs]
        self.azimuth_per_step = self.azimuth_per_step[:, idxs]
        self.dist_per_step = self.dist_per_step[:, idxs]
        self.speed_per_step = self.speed_per_step[:, idxs]
        self.fuel_per_step = self.fuel_per_step[:, idxs]

        self.current_azimuth = self.current_variant[idxs]
        self.current_variant = self.current_variant[idxs]
        self.full_dist_traveled = self.full_dist_traveled[idxs]
        self.full_time_traveled = self.full_time_traveled[idxs]
        self.full_fuel_consumed = self.full_fuel_consumed[idxs]
        self.time = self.time[idxs]

        #print('last_azimuth', self.last_azimuth)
        #print('inx', idxs)

        # print("rpm = ",boat.get_rpm())
        # print("Used fuel", boat.get_fuel_per_time(delta_time))

    def define_variants_per_step(self):
        self.define_variants()

    def set_pruning_settings(self, sector_deg_half, seg):
        self.prune_sector_deg_half = sector_deg_half
        self.prune_segments = seg

    def set_variant_segments(self, seg, inc):
        self.variant_segments = seg
        self.variant_increments_deg = inc

    def get_current_azimuth(self):
        return self.current_variant

    def get_current_lats(self):
        return self.lats_per_step[0, :]

    def get_current_lons(self):
        return self.lons_per_step[0, :]

    def get_current_speed(self):
        return self.speed_per_step[0]

    def get_wind_functions(self, wt):
        debug = False
        winds = wt.get_wind_function((self.get_current_lats(), self.get_current_lons()), self.time[0])
        if (debug):
            print('obtaining wind function for position: ', self.get_current_lats(), self.get_current_lons())
            print('time', self.time[0])
            print('winds', winds)
        return winds

    def check_settings(self):
        if (self.variant_segments/2*self.variant_increments_deg >= self.prune_sector_deg_half):
            raise ValueError('Prune sector does not contain all variants. Please adjust settings. (variant_segments=' +
                             str(self.variant_segments) + ', variant_increments_deg=' + str(self.variant_increments_deg)
                             + ', prune_sector_deg_half=' + str(self.prune_sector_deg_half))

    def get_final_index(self):
        idx = np.argmax(self.full_dist_traveled)
        return idx

    def terminate(self, boat : Boat, wt: WeatherCond):
        self.lats_per_step=np.flip(self.lats_per_step,0)
        self.lons_per_step=np.flip(self.lons_per_step,0)
        self.azimuth_per_step=np.flip(self.azimuth_per_step,0)
        self.dist_per_step=np.flip(self.dist_per_step,0)
        self.speed_per_step=np.flip(self.speed_per_step,0)
        route = RoutingAlg.terminate(self, boat, wt)

        self.check_isochrones(route)
        return route

    def update_time(self, delta_time):
        self.full_time_traveled += delta_time
        self.time += dt.timedelta(seconds=delta_time)

    def update_position(self, dist):
        debug = False

        move = geod.direct(self.get_current_lats(), self.get_current_lons(), self.current_variant, dist)    #calculate new isochrone, update position and distance traveled
        self.lats_per_step = np.vstack((move['lat2'], self.lats_per_step))
        self.lons_per_step = np.vstack((move['lon2'], self.lons_per_step))
        self.dist_per_step = np.vstack((dist, self.dist_per_step))
        self.azimuth_per_step = np.vstack((self.current_variant, self.azimuth_per_step))

        if (debug):
            print('path of this step' +
                 # str(move['lat1']) +
                 # str(move['lon1']) +
                  str(move['lat2']) +
                  str(move['lon2']))
            print('dist', dist)
            print('bs=', self.speed_per_step)

        start_lats = np.repeat(self.start[0], self.lats_per_step.shape[1])
        start_lons = np.repeat(self.start[1], self.lons_per_step.shape[1])
        gcrs = geod.inverse(start_lats, start_lons, move['lat2'], move['lon2'])       #calculate full distance traveled, azimuth of gcr connecting start and new position
        self.current_variant = gcrs['azi1']
        self.current_azimuth = gcrs['azi1']

        # remove those which ended on land
        is_on_land = globe.is_land(move['lat2'], move['lon2'])
        #print('is_on_land', is_on_land)
        gcrs['s12'][is_on_land] = 0
        crosses_land = self.crosses_land()
        gcrs['s12'][crosses_land] = 0
        self.full_dist_traveled = gcrs['s12']






        # for i in range(int((x2 - x1) / STEP) + 1): #62.3, 17.6, 59.5, 24.6
        #     try:
        #         x = x1 + i * STEP
        #         y = (y1 - y2) / (x1 - x2) * (x - x1) + y1
        #     except:
        #         continue
        #     is_on_land = globe.is_land(float(x), float(y))
        #     print(is_on_land)
        #     # if not is_on_land:
        #     # print("in water")
        #
        #     if is_on_land:
        #         # print("crosses land")
        #
        #         return True

        # print('isonland',is_on_land)
        # z = globe.is_land(lats, lons)
        # print('value of z',type(z))
        # if z=='True':
        #     is_on_land = globe.is_land(move['lats2'], move['lons2'])
        #     print(is_on_land)

        # print(self)

    def update_fuel(self, delta_fuel):
        self.fuel_per_step = np.vstack((delta_fuel,  self.fuel_per_step))
        for i in range(0,self.full_fuel_consumed.shape[0]):
            self.full_fuel_consumed[i] += delta_fuel[i]

    def check_isochrones(self, route : RouteParams):
        pass

    def get_delta_variables(self, boat, wind, bs):
        pass