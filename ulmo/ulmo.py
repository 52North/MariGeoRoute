import xarray as xr
#import rioxarray as rio
#import matplotlib.pyplot as plt
import math
import numpy as np
import datetime


def diff_vec(waypoint, point):
    wp_x, wp_y = waypoint
    p_x, p_y = point
    return(wp_x - p_x, wp_y - p_y)

def speed(vec):
    x, y = vec
    return math.sqrt(x**2 + y**2)

def angle(vec):
    x, y = vec
    return math.degrees(math.atan2(x,y))

def norm(vec):
    s = speed(vec)
    x, y = vec
    return(x/s, y/s)

def geo_coords(mask):
    l, y, x = np.where(mask>0)
    x_coords = mask.coords['x'].values[x]
    y_coords = mask.coords['y'].values[y]

    coords=[]
    for i, x_c in enumerate(x_coords):
        #print(i, x)
        coords.append((x_c, y_coords[i]))

    return coords


def neighbours(point):
    # gen_0 = (5.25, 39)
    # gen = [[gen_0]]
    res=0.25
    x, y = point
    px=x+res
    mx=x-res
    py=y+res
    my=y-res

    xs=[x,px,mx]
    ys=[y,py,my]
    return [(a, b) for a in xs for b in ys]


def unlist(l):
    return [item for sublist in l for item in sublist]


def generations(point0, geo_coords):
    # point0 = (5.25, 39)
    # point0 = (8, 39)
    gen = [[point0]]

    old_points = unlist(gen)
    new_points = neighbours(point0)
    new_gen = [p for p in new_points if p not in old_points]
    gen.append(new_gen)

    while any(item in geo_coords for item in new_gen):
        buffer= []
        old_points = unlist(gen)
        for point in gen[-1]:
            new_points = neighbours(point)
            buffer.append(new_points)
        ul_buffer=list(set(unlist(buffer)))
        new_gen=[p for p in ul_buffer if p not in old_points]

        gen.append(new_gen)


    erg=[]
    for g in gen:
        legit = [c for c in g if c in geo_coords]
        erg.append(legit)

    return(erg)


def func(l):
    return [4+x*0.30*math.e*0.111*x for x in l]


def manfred(t_start, gens, geo_coords, norm_vecs, nc_array):
    t_delta = datetime.timedelta(hours=3)
    if len(gens)>len(nc_array.time):
        t_series = [t_start + i * t_delta for i in range(len(nc_array.time)-1)]
    else:
        t_series = [t_start + i * t_delta for i in range(len(gens))]
    print(len(gens))
    # t_series = [t_start + i * t_delta for i in range(30)]

    new_speed = func(range(len(gens)))
    new_speed = [24 if x > 24 else x for x in new_speed]

    for k, gens in enumerate(gens):
        for gen in gens:
            lon, lat = gen
            u, v = norm_vecs[geo_coords.index(gen)]
            for i, t in enumerate(t_series[k:]):
                nc_array['u-component_of_wind_height_above_ground'].loc[dict(latitude=lat, longitude=lon, time=t)] = \
                new_speed[i] * u
                nc_array['v-component_of_wind_height_above_ground'].loc[dict(latitude=lat, longitude=lon, time=t)] = \
                new_speed[i] * v

    return nc_array




# https://tolkiengateway.net/wiki/Ulmo
def ulmo(gfs, nc_mask, waypoint, point, area, t_start, outfile=None):

    # #LON LAT
    # # waypoint wind blows to
    # waypoint=(12.789889357194918, 37.09280205794121)
    # # startpoint within the storm geometry
    # point = (8, 39)
    # #read data
    # gfs = xr.open_dataset("./daten/env/gfs.nc")
    # #read storm geometry
    # nc_mask = xr.open_dataset('./daten/mask.nc')


    mask_val = nc_mask.__xarray_dataarray_variable__
    m = mask_val.where(mask_val == area, drop=True)

    # get all coords of mask geometry
    coords = geo_coords(m)
    # normalize vecs between each point and waypoint
    norm_vecs = [norm(diff_vec(waypoint, vec)) for vec in coords]
    #get all generations
    gens = generations(point, coords)
    #when will bad weather start
    # t_start= datetime.datetime(year=2023, month=10, day=31, hour=3)
    #manipulate data
    manni = manfred(t_start, gens, coords, norm_vecs, gfs)

    if outfile:
        manni.to_netcdf(f"{outfile}")

    return manni

gfs = xr.open_dataset("./simulation/II/daten/env/gfs.nc")
nc_mask = xr.open_dataset('./simulation/II/daten/mask.nc')
#t_start= datetime.datetime(year=2023, month=10, day=31, hour=3)


#reduce wind
gfs["u-component_of_wind_height_above_ground"] = gfs["u-component_of_wind_height_above_ground"]/10
gfs["v-component_of_wind_height_above_ground"] = gfs["v-component_of_wind_height_above_ground"]/10

med = ulmo(gfs, nc_mask, (12.789889357194918, 37.09280205794121), (8, 39), 1, datetime.datetime(year=2023, month=10, day=31, hour=3))
indian = ulmo(med, nc_mask, (87.85821706039933, 5.609412749153263), (93, 5), 2, datetime.datetime(year=2023, month=10, day=30, hour=3))
npazific = ulmo(indian, nc_mask, (-127.62806387974446, 39.301657626529675), (-133, 45), 3, datetime.datetime(year=2023, month=10, day=29, hour=15), outfile="./simulation/II/daten/magna_mani.nc")

#for vis:
wind_spd = np.sqrt(np.power(npazific["u-component_of_wind_height_above_ground"],2) + np.power(gfs["v-component_of_wind_height_above_ground"],2))