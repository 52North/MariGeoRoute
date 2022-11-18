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
        debug = True
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

        print('full dist travelled', self.full_dist_traveled)
        print('Indexes that passed', idxs)

        # Return a trimmed isochrone
        lats_new = self.lats_per_step[:, idxs]
        lons_new = self.lons_per_step[:, idxs]
        var_new = self.azimuth_per_step[:, idxs]
        dist_new = self.dist_per_step[:, idxs]
        speed_new = self.speed_per_step[:, idxs]
        curr_azi_new = self.current_variant[idxs]
        full_dist_new = self.full_dist_traveled[idxs]

        self.lats_per_step = lats_new
        self.lons_per_step = lons_new
        self.azimuth_per_step = var_new
        self.dist_per_step = dist_new
        self.current_azimuth = curr_azi_new
        self.current_variant = curr_azi_new
        self.full_dist_traveled = full_dist_new
        self.speed_per_step = speed_new

        #print('last_azimuth', self.last_azimuth)
        #print('inx', idxs)

        # print("rpm = ",boat.get_rpm())
        # print("Used fuel", boat.get_fuel_per_time(delta_time))

    def define_variants_per_step(self):
        self.define_variants()

    def define_initial_variants(self):
        self.full_time_traveled = np.repeat(0., self.variant_segments + 1, axis=0)

    def get_current_azimuth(self):
        return self.current_variant

    def crosses_land(self):
        debug = False

        LandCrossingSteps = 10
        delta_lats = (self.lats_per_step[0, :] - self.lats_per_step[1, :]) / LandCrossingSteps
        delta_lons = (self.lons_per_step[0, :] - self.lons_per_step[1, :]) / LandCrossingSteps
        x0 = self.lats_per_step[1, :]
        y0 = self.lons_per_step[1, :]
        print('lats_per_step shape',  self.lats_per_step.shape[1] )
        is_on_land = [False for i in range(0, self.lats_per_step.shape[1])]

        if(debug):
            print('Moving from (' + str(self.lats_per_step[1, :]) + ',' + str(self.lons_per_step[1, :]) + ') to (' + str(self.lats_per_step[0, :]) + ',' + str(self.lons_per_step[0, :]))
            print('x0=' + str(x0) + ', y0=' + str(y0))
            print('is_on_land', is_on_land)
            print('delta_lats', delta_lats)
            print('delta_lons', delta_lons)

        for iStep in range(0, LandCrossingSteps):
            x = x0 + delta_lats
            y = y0 + delta_lons
            if (debug):
                print('     iStep=', iStep)
                print('     x=', x)
                print('     y=', y)

            is_on_land_temp = globe.is_land(x,y)
            print('is_on_land_temp', is_on_land_temp)
            is_on_land = is_on_land + is_on_land_temp
            print('is_on_land', is_on_land)
            x0 = x
            y0 = y


        #if not ((round(x0.all,8) == round(self.lats_per_step[0, :].all) and (x0.all == self.lons_per_step[0, :].all)):
        #    exc = 'Did not check destination, only checked lat=' + str(x0) + ', lon=' + str(y0)
        #    raise ValueError(exc)

        return is_on_land

    def get_wind_functions(self, wt):
        debug = False
        winds = wt.get_wind_function((self.current_lats, self.current_lons), self.time[0])
        if(debug):
            print('obtaining wind function for position: ', self.current_lats, self.current_lons)
            print('time', self.time[0])
            print('winds', winds)
        return winds

    def get_final_index(self):
        idx = np.argmax(self.full_dist_traveled)
        return idx

    def terminate(self, boat : Boat):
        self.lats_per_step=np.flip(self.lats_per_step,0)
        self.lons_per_step=np.flip(self.lons_per_step,0)
        self.azimuth_per_step=np.flip(self.azimuth_per_step,0)
        self.dist_per_step=np.flip(self.dist_per_step,0)
        self.speed_per_step=np.flip(self.speed_per_step,0)
        route = RoutingAlg.terminate(self, boat)

        self.check_isochrones(route)
        return route

    def check_isochrones(self, route : RouteParams):
        pass
