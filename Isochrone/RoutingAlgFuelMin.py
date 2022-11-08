import numpy as np
import datetime as dt
import utils as ut
from polars import Boat
from typing import NamedTuple
from geovectorslib import geod
from weather import wind_function
from global_land_mask import globe
from scipy.stats import binned_statistic
from routeparams import RouteParams
from isochrone import RoutingAlg
import utils

class RoutingAlgFuelMin(RoutingAlg):

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

    def current_position(self):
        print('CURRENT POSITION')
        print('lats = ', self.current_lats)
        print('lons = ', self.current_lons)
        print('azimuth = ', self.current_azimuth)
        print('full_time_traveled = ', self.full_time_traveled)

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

        print('az after repeat', self.azimuth_per_step.shape)


    def get_current_azimuth(self):
        return self.current_azimuth[0]

    def update_position(self):
        self.current_lats = self.lats_per_step[self.count,:]
        self.current_lons = self.lons_per_step[self.count,:]
        self.current_azimuth=self.azimuth_per_step[self.count+1,:]

    def update_time(self, delta_time, bs):
        gcrs = geod.inverse(self.lats_per_step[self.count,:], self.lons_per_step[self.count,:], self.lats_per_step[self.count+1,:], self.lons_per_step[self.count+1,:])
        dist = gcrs['s12']
        #self.time += dt.timedelta(seconds=dist/bs)

        print('dist=', dist)
        print('bs=', bs)

        delta_time_calc=dist/bs
        print('dt=', delta_time_calc)
        delta_time_calc=np.round(delta_time_calc/100)*100
        if not (delta_time == delta_time_calc[0]):
            raise ValueError('delta_time=' + str(delta_time) + ' delta_time_calc=' + str(delta_time_calc))
        self.full_time_traveled += delta_time_calc

    def update_dist(self, delta_time, bs, current_lats, current_lons):
        #return {'lat2' : self.lats_per_step[self.count,:], 'lon2' : self.lons_per_step[self.count,:]}
        pass

    def get_final_index(self):
        return 0    #dummy

    def terminate(self, boat : Boat):
        route = RoutingAlg.terminate(self, boat)
        return route
