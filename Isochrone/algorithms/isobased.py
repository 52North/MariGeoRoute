import datetime as dt
import logging

import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
import matplotlib.pyplot as plt
from geovectorslib import geod
from global_land_mask import globe
from scipy.stats import binned_statistic

import utils.graphics as graphics
import utils.formatting as form
from ship.ship import Boat
from algorithms.routingalg import RoutingAlg
from routeparams import RouteParams
from weather import WeatherCond

logger = logging.getLogger('WRT.Pruning')

class IsoBased(RoutingAlg):

    def __init__(self, start, finish, time, figurepath=""):
        RoutingAlg.__init__(self, start, finish, time, figurepath)
        self.current_variant=self.current_azimuth
        self.is_last_step = False

    def print_init(self):
        RoutingAlg.print_init(self)

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

    def pruning(self, trim, bins):
        debug = False
        valid_pruning_segments = -99

        if (debug):
            print('binning for pruning', bins)
            print('current courses', self.current_azimuth)

        idxs = []
        bin_stat, bin_edges, bin_number = binned_statistic(
            self.current_variant, self.full_dist_traveled, statistic=np.nanmax, bins=bins)

        if trim:
            for i in range(len(bin_edges) - 1):
                try:
                    if(bin_stat[i]==0):
                        #form.print_step('Pruning: sector ' + str(i) + 'is null (binstat[i])=' + str(bin_stat[i]) + 'full_dist_traveled=' + str(self.full_dist_traveled))
                        continue
                    idxs.append(
                        np.where(self.full_dist_traveled == bin_stat[i])[0][0])
                except IndexError:
                    pass
            idxs = list(set(idxs))
        else:
            for i in range(len(bin_edges) - 1):
                idxs.append(np.where(self.full_dist_traveled == bin_stat[i])[0])
            idxs = list(set([item for subl in idxs for item in subl]))

        if (debug):
            print('full_dist_traveled', self.full_dist_traveled)
            print('Indexes that passed', idxs)

        valid_pruning_segments = len(idxs)
        if(valid_pruning_segments==0):
            logger.error(' All pruning segments fully constrained for step ' + str(self.count) + '!')
        elif (valid_pruning_segments < self.prune_segments * 0.1):
            logger.warning(' More than 90% of pruning segments constrained for step ' + str(self.count) + '!')
        elif(valid_pruning_segments < self.prune_segments * 0.5):
            logger.warning(' More than 50% of pruning segments constrained for step ' + str(self.count) + '!')

        # Return a trimmed isochrone
        try:
            self.lats_per_step = self.lats_per_step[:, idxs]
            self.lons_per_step = self.lons_per_step[:, idxs]
            self.azimuth_per_step = self.azimuth_per_step[:, idxs]
            self.dist_per_step = self.dist_per_step[:, idxs]
            self.shipparams_per_step.select(idxs)

            self.starttime_per_step = self.starttime_per_step[:, idxs]

            self.current_azimuth = self.current_variant[idxs]
            self.current_variant = self.current_variant[idxs]
            self.full_dist_traveled = self.full_dist_traveled[idxs]
            self.full_time_traveled = self.full_time_traveled[idxs]
            self.full_fuel_consumed = self.full_fuel_consumed[idxs]
            self.time = self.time[idxs]
        except IndexError:
            raise Exception('Pruned indices running out of bounds.')

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

        if (debug): print('mean azimuth', new_azi['azi1'])

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

        self.pruning(trim, bins)

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
        if ((self.variant_segments % 2)!=0):
            raise ValueError('Please provide an even number of variant segments, you chose: ' + str(self.variant_segments))

        if ((self.prune_segments % 2)!=0):
            raise ValueError(
                'Please provide an even number of prune segments, you chose: ' + str(self.prune_segments))

    def get_final_index(self):
        idx = np.argmax(self.full_dist_traveled)
        return idx

    def terminate(self, boat : Boat, wt: WeatherCond):
        self.lats_per_step=np.flip(self.lats_per_step,0)
        self.lons_per_step=np.flip(self.lons_per_step,0)
        self.azimuth_per_step=np.flip(self.azimuth_per_step,0)
        self.dist_per_step=np.flip(self.dist_per_step,0)
        self.starttime_per_step=np.flip(self.starttime_per_step,0)
        self.shipparams_per_step.flip()

        route = RoutingAlg.terminate(self, boat, wt)

        self.check_isochrones(route)
        return route

    def update_time(self, delta_time):
        self.full_time_traveled += delta_time
        self.time += dt.timedelta(seconds=delta_time)

    def check_bearing(self, dist):
        debug = False

        nvariants = self.get_current_lons().shape[0]
        dist_to_dest =  geod.inverse(
            self.get_current_lats(),
            self.get_current_lons(),
            np.full(nvariants, self.finish[0]),
            np.full(nvariants, self.finish[1])
        )
        if(debug):
            print('dist_to_dest:', dist_to_dest['s12'])
            print('dist traveled:', dist)

        reaching_dest = dist_to_dest['s12'] < dist

        if(debug):
            print('reaching dest:', reaching_dest)

        if(np.any(reaching_dest)):
            self.is_last_step = True
            new_lat = np.full(nvariants, self.finish[0])
            new_lon = np.full(nvariants, self.finish[1])
            return {'azi2': dist_to_dest['azi1'], 'lat2': new_lat, 'lon2': new_lon, 'iterations' : -99}     #compare to  'return {'lat2': lat2, 'lon2': lon2, 'azi2': azi2, 'iterations': iterations}' by geod.direct

        move = geod.direct(self.get_current_lats(), self.get_current_lons(), self.current_variant, dist)   
        #form.print_step('move=' + str(move),1)
        return move

    def check_constraints(self, move, constraint_list):
        debug = False

        is_constrained = [False for i in range(0, self.lats_per_step.shape[1])]
        if(debug): form.print_step('shape is_constraint before checking:' + str(len(is_constrained)),1)
        is_constrained = constraint_list.safe_crossing(self.lats_per_step[0], move['lat2'], self.lons_per_step[0], move['lon2'], self.time, is_constrained)
        if(debug): form.print_step('is_constrained after checking' + str(is_constrained),1)
        return is_constrained

    def update_position(self, move, is_constrained, dist):
        debug = False
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

        gcrs['s12'][is_constrained] = 0
        self.full_dist_traveled = gcrs['s12']
        if(debug):
            print('full_dist_traveled:', self.full_dist_traveled)

    def update_fuel(self, delta_fuel):
        self.shipparams_per_step.set_fuel(np.vstack((delta_fuel,  self.shipparams_per_step.get_fuel())))
        for i in range(0,self.full_fuel_consumed.shape[0]):
            self.full_fuel_consumed[i] += delta_fuel[i]

    def check_isochrones(self, route : RouteParams):
        pass

    def get_delta_variables(self, boat, wind, bs):
        pass

    def get_delta_variables_netCDF_last_step(self, boat, wind, bs):
        pass

    def init_fig(self, wt):
        level_diff = 10
        plt.rcParams['font.size'] = 20

        depth = wt.ds['depth'].where(wt.ds.depth < 0, drop=True)

        self.fig, ax = plt.subplots(figsize=(12, 10))
        ax.axis('off')
        ax.xaxis.set_tick_params(labelsize='large')
        ax = self.fig.add_subplot(111, projection=ccrs.PlateCarree())
        cp = depth.plot.contourf(ax=ax, levels=np.arange(-100, 0, level_diff),
                                 transform=ccrs.PlateCarree())
        self.fig.colorbar(cp, ax=ax, shrink=0.7, label='Wassertiefe (m)', pad=0.1)

        self.fig.subplots_adjust(
            left=0.1,
            right=1.2,
            bottom=0,
            top=1,
            wspace=0,
            hspace=0)
        ax.add_feature(cf.LAND)
        ax.add_feature(cf.COASTLINE)
        ax.gridlines(draw_labels=True)

        ax.plot( self.start[1],self.start[0], marker="o", markerfacecolor="orange", markeredgecolor="orange",markersize=10)
        ax.plot( self.finish[1],self.finish[0], marker="o", markerfacecolor="orange", markeredgecolor="orange",markersize=10)

        self.route_ensemble = []
        for iRoute in  range(0,self.prune_segments * self.variant_segments):
            route, = ax.plot(self.lons_per_step[:, 0], self.lats_per_step[:, 0], color = "firebrick")
            self.route_ensemble.append(route)

        gcr = graphics.get_gcr_points(self.start[0], self.start[1], self.finish[0], self.finish[1], n_points=10)
        lats_gcr = [x[0] for x in gcr]
        lons_gcr = [x[1] for x in gcr]
        ax.plot(lons_gcr, lats_gcr, color = "orange")
        plt.title('')

        final_path = self.figure_path + '/fig0.png'
        print('Saving start figure to ', final_path)
        plt.savefig(final_path)

    def update_fig(self, status):
        fig = self.fig

        for iRoute in range(0,self.prune_segments * self.variant_segments):
            if iRoute>= self.lats_per_step.shape[1]:
                self.route_ensemble[iRoute].set_xdata([0])
                self.route_ensemble[iRoute].set_ydata([0])
            else:
                self.route_ensemble[iRoute].set_xdata(self.lons_per_step[:,iRoute])
                self.route_ensemble[iRoute].set_ydata(self.lats_per_step[:, iRoute])

            fig.canvas.draw()
            fig.canvas.flush_events()

        gcr = graphics.get_gcr_points(self.start[0], self.start[1], self.finish[0], self.finish[1], n_points=10)
        lats_gcr = [x[0] for x in gcr]
        lons_gcr = [x[1] for x in gcr]
        self.fig.get_axes()[1].plot(lons_gcr, lats_gcr, color = "orange")

        final_path = self.figure_path + '/fig' + str(self.count) + status + '.png'
        print('Saving updated figure to ', final_path)
        plt.savefig(final_path)

