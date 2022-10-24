"""Module to create map with route."""
import numpy as np
"""Cartopy is a Python package designed for geospatial data processing in order to produce maps 
and other geospatial data analyses"""
import cartopy.crs as ccrs
import cartopy.feature as cf
from itertools import chain
from geovectorslib import geod
from matplotlib.figure import Figure

"""lat1 : initial latitude 
   lat2 : Final latitude
   lon1 : initial longitude 
   lon2 : Final Longitude """
def get_gcr_points(lat1, lon1, lat2, lon2, n_points=10):
    """Discretize gcr between two scalar coordinate points."""
    points = [(lat1, lon1)]

    inv = geod.inverse([lat1], [lon1], [lat2], [lon2])
    dist = inv['s12'] / (n_points)

    for i in range(n_points):
        dir = geod.direct(lat1, lon1, inv['azi1'], dist)
        points.append((dir['lat2'][0], dir['lon2'][0]))
        lat1 = dir['lat2'][0]
        lon1 = dir['lon2'][0]
        inv = geod.inverse([lat1], [lon1], [lat2], [lon2])

    return points


def create_maps(lat1, lon1, lat2, lon2, dpi, winds, n_maps):
    """Return map figure."""
    fig = Figure(
        figsize=(1600 / dpi, 800 * n_maps / dpi),
        dpi=dpi)
    fig.set_constrained_layout_pads(
        w_pad=4. / dpi,
        h_pad=4. / dpi)

    """Add gcrs between provided points to the map figure."""
    path = get_gcr_points(lat1, lon1, lat2, lon2, n_points=10)
    print(path)
    for i in range(n_maps):
        ax = fig.add_subplot(n_maps+1, 1, i+1, projection=ccrs.PlateCarree())
        ax.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
        ax.add_feature(cf.LAND)
        ax.add_feature(cf.OCEAN)
        ax.add_feature(cf.COASTLINE)
        ax.gridlines(draw_labels=True)

        hour = i // 3 * 3
        u, v, lats, lons = winds[int(hour)]
        ax.barbs(lons, lats, u, v, length=5,
                 sizes=dict(emptybarb=0.25, spacing=0.2, height=0.5),
                 linewidth=0.95)

        lats = [x[0] for x in path]
        lons = [x[1] for x in path]
        ax = fig.get_axes()[0]
        ax.plot(lons, lats, 'r-', transform=ccrs.PlateCarree())
    return fig


def create_map(lat1, lon1, lat2, lon2, dpi):
    """Return map figure."""
    fig = Figure(
        figsize=(1200 / dpi, 420 / dpi),
        dpi=dpi)
    fig.set_constrained_layout_pads(
        w_pad=4. / dpi,
        h_pad=4. / dpi)
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    fig.subplots_adjust(
        left=0.05,
        right=0.95,
        bottom=0,
        top=1,
        wspace=0,
        hspace=0)
    #ax.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
    ax.add_feature(cf.LAND)
    ax.add_feature(cf.OCEAN)
    ax.add_feature(cf.COASTLINE)
    ax.gridlines(draw_labels=True)
    return fig


def plot_barbs(fig, winds, hour):
    """Add barbs to the map figure."""
    u, v, lats, lons = winds[int(hour)]

    ax = fig.get_axes()[0]
    ax.barbs(lons, lats, u, v, length=5,
             sizes=dict(emptybarb=0.25, spacing=0.2, height=0.5),
             linewidth=0.95)
    # ax.quiver(lons, lats, u, v)
    return fig


def plot_gcr(fig, lat1, lon1, lat2, lon2):
    """Add gcrs between provided points to the map figure."""
    path = get_gcr_points(lat1, lon1, lat2, lon2, n_points=10)
    lats = [x[0] for x in path]
    lons = [x[1] for x in path]

    ax = fig.get_axes()[0]
    ax.plot(lons, lats, 'g', transform=ccrs.PlateCarree())
    return fig


def plot_isochrones(fig, iso3):
    """
    Add isochrone to the map figure.

    Input: dictionary from move_boat_direct
    """
    ax = fig.get_axes()[0]
    idx = np.argmax(iso3.s02)
    # idx=np.int64(69)
    sortidx=np.sort(iso3.s02)
    idx2=sortidx[-5]
    idx3=np.where(iso3.s02==idx2)

    idx4=idx3[0]

    lats = iso3.lats1[:,idx4]
    type(lats)
    #print(len(lats))
    #idx = np.int64(90)
   # idx = np.argmax(iso3.s02)
    lons = iso3.lons1[:,idx4]
    flag1=iso3.lons1
    lonndarraytolist=flag1.tolist()
    flag2=iso3.lats1
    latsndtolist=flag2.tolist()


     # converting 2d list into 1d
     # using chain.from_iterables
    # flatten_list = list(chain.from_iterable(a))
    #
    # # printing flatten_list
    # print("final_result", str(flatten_list))
    # print('ppppp',flatten_list.index('35.18810965867689'))
    #print('========nd araay of latitude ========',a)

    #

    #print(lons, 'lons=im from graphics')  #59.6,28.4
    #print('type of iso3.lons',type(iso3.lats1))
    geeky_file = open('/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Dicts/dict4.txt', 'wt')
    #geeky_file.write(str(iso3.lons1[:,1]))

    geeky_file.close()
    ax = fig.get_axes()[0]
    # for i in range(len(lats)):
    #     ax.plot(lons[i], lats[i], 'ro')
    ax.plot(lons, lats, 'magenta', transform=ccrs.PlateCarree())
    return fig
