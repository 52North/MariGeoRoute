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

class RoutingAlgTimeFuelMin(RoutingAlg):

    def __init__(self, route : RouteParams, time):
        RoutingAlg.__init__(self, route.start, route.finish, time)
        self.lats_per_step = route.lats_per_step
        self.lons_per_step = route.lons_per_step
        self.dist_per_step = route.dists_per_step
        self.full_dist_traveled = route.full_dist_traveled

        self.azimuth_per_step = route.azimuths_per_step[:, np.newaxis]
        self.current_variant = route.rpm

        self.lats_per_step = self.lats_per_step[:, np.newaxis]
        self.lons_per_step = self.lons_per_step[:, np.newaxis]
        self.dist_per_step = self.dist_per_step[:, np.newaxis]
        self.current_azimuth = np.array([self.azimuth_per_step[1]])

    def pruning(self,  x, y, trim=True):
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

        idxs = []
        bin_stat, bin_edges, bin_number = binned_statistic(
            self.last_azimuth, self.full_dist_traveled, statistic=np.nanmax, bins=bins)

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


        # Return a trimmed isochrone
        lats_new = self.lats_per_step[:, idxs]
        lons_new = self.lons_per_step[:, idxs]
        var_new = self.variants[:, idxs]
        dist_new = self.dist_per_step[:, idxs]
        curr_azi_new = self.last_azimuth[idxs]
        full_dist_new = self.full_dist_traveled[idxs]

        self.lats_per_step = lats_new
        self.lons_per_step = lons_new
        self.variants = var_new
        self.dist_per_step = dist_new
        self.last_azimuth = curr_azi_new
        self.full_dist_traveled = full_dist_new

        #print('last_azimuth', self.last_azimuth)
        #print('inx', idxs)

        # print("rpm = ",boat.get_rpm())
        # print("Used fuel", boat.get_fuel_per_time(delta_time))

    def define_initial_variants(self):
        self.define_variants()
        self.full_time_traveled = np.repeat(0., self.variant_segments + 1, axis=0)
        self.full_dist_traveled = np.repeat(self.full_dist_traveled, self.variant_segments + 1, axis=0)
        self.time = np.repeat(self.time, self.variant_segments + 1, axis=0)

    def get_current_azimuth(self):
        return self.azimuth_per_step[self.count+1]

    def update_position(self):
        self.current_lats = self.lats_per_step[self.count+1,:]
        self.current_lons = self.lons_per_step[self.count+1,:]

    def update_time(self, delta_time, bs):
        debug = True

        gcrs = geod.inverse(self.lats_per_step[self.count,:], self.lons_per_step[self.count,:], self.lats_per_step[self.count+1,:], self.lons_per_step[self.count+1,:])
        dist = gcrs['s12']
        #self.time += dt.timedelta(seconds=dist/bs)

        delta_time_calc=dist/bs
        delta_time_calc=np.round(delta_time_calc/100)*100
        if not (delta_time == delta_time_calc[0]):
            raise ValueError('delta_time=' + str(delta_time) + ' delta_time_calc=' + str(delta_time_calc))

        for iTime in range(0,self.variant_segments+1):
                self.time[iTime]+=dt.timedelta(seconds=delta_time_calc[0])
                self.full_time_traveled[iTime]+=delta_time_calc[0]

        if(debug):
            print('dist', dist)
            print('bs', bs)
            print('time = ',self.time)
            print('delta_time_calc = ', delta_time_calc)

    def update_dist(self, delta_time, bs, current_lats, current_lons):
        #return {'lat2' : self.lats_per_step[self.count,:], 'lon2' : self.lons_per_step[self.count,:]}
        pass

    def get_wind_functions(self,wt):
        debug = False
        twa = np.zeros(self.variant_segments+1)
        tws = np.zeros(self.variant_segments+1)

        for i in range(0,self.variant_segments+1):
            winds = wt.get_wind_function((self.current_lats, self.current_lons), self.time[i])
            twa[i] = winds['twa'][0]
            tws[i] = winds['tws'][0]

        if(debug):
            print('obtaining wind function for current position', self.current_lats, self.current_lons)
            print('time:', self.time[0])
            print('wind', winds)

        winds =  {'twa' : twa, 'tws' : tws}
        return winds

    def get_final_index(self):
        return 0    #dummy

    def terminate(self, boat : Boat):
        route = RoutingAlg.terminate(self, boat)
        return route
