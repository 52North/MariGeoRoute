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


def neighbours(point, res):
    # gen_0 = (5.25, 39)
    # gen = [[gen_0]]
    # res=0.25
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


def generations(point0, geo_coords, res):
    # point0 = (5.25, 39)
    # point0 = (8, 39)
    gen = [[point0]]

    old_points = unlist(gen)
    new_points = neighbours(point0, res)
    new_gen = [p for p in new_points if p not in old_points]
    gen.append(new_gen)

    while any(item in geo_coords for item in new_gen):
        buffer= []
        old_points = unlist(gen)
        for point in gen[-1]:
            new_points = neighbours(point, res)
            buffer.append(new_points)
        ul_buffer=list(set(unlist(buffer)))
        new_gen=[p for p in ul_buffer if p not in old_points]

        gen.append(new_gen)


    erg=[]
    for g in gen:
        legit = [c for c in g if c in geo_coords]
        erg.append(legit)

    return(erg)


def wind_grow(l):
    return [4+x*0.30*math.e*0.111*x for x in l]

def wave_grow(wind):
    #Bretschneider C. L. (1952). The generation and decay of wind waves in deep water. EOS Trans. Am. Geophys. Union 33, 381–389. doi: 10.1029/TR033i003p00381
    return [(0.3 * vel**2) / 9.81 for vel in wind]


def wind_vectors_manip(t_start, gens, geo_coords, norm_vecs, nc_array):
    t_delta = datetime.timedelta(hours=3)
    if len(gens)>len(nc_array.time):
        t_series = [t_start + i * t_delta for i in range(len(nc_array.time)-1)]
    else:
        t_series = [t_start + i * t_delta for i in range(len(gens))]
    print(len(gens))
    # t_series = [t_start + i * t_delta for i in range(30)]

    new_speed = wind_grow(range(len(gens)))
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


def waves_manip(t_start, gens, geo_coords, angles, nc_array):
    t_delta = datetime.timedelta(hours=3)
    if len(gens)>len(nc_array.time):
        t_series = [t_start + i * t_delta for i in range(len(nc_array.time)-1)]
    else:
        t_series = [t_start + i * t_delta for i in range(len(gens))]
    print(len(gens))
    # t_series = [t_start + i * t_delta for i in range(30)]

    new_speed = wind_grow(range(len(gens)))
    new_speed = [24 if x > 24 else x for x in new_speed]
    new_waves = wave_grow(new_speed)


    for k, gens in enumerate(gens):
        for gen in gens:
            lon, lat = gen
            a = angles[geo_coords.index(gen)]
            for i, t in enumerate(t_series[k:]):
                nc_array['VMDR'].loc[dict(latitude=lat, longitude=lon, time=t)] = a
                nc_array['VHM0'].loc[dict(latitude=lat, longitude=lon, time=t)] = new_waves[i]

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
    gens = generations(point, coords, 0.25)
    #when will bad weather start
    # t_start= datetime.datetime(year=2023, month=10, day=31, hour=3)
    #manipulate data
    manni = wind_vectors_manip(t_start, gens, coords, norm_vecs, gfs)

    if outfile:
        manni.to_netcdf(f"{outfile}")

    return manni


def ulmo_wave(cmems, nc_mask, waypoint, point, area, t_start, outfile=None):
    # w = cmems.coarsen(latitude=3, longitude=3, boundary='pad', coord_func='min').mean()
    # lo = np.array([-180 + 0.25 * i for i in range(1440)])
    # la = np.array([-80 + 0.25 * i for i in range(681)])
    # waves_dwnsampled = w.assign_coords(longitude=lo, latitude=la)

    mask_val = nc_mask.__xarray_dataarray_variable__
    m = mask_val.where(mask_val == area, drop=True)
    coords = geo_coords(m)
    angles = [angle(norm(diff_vec(waypoint, vec))) for vec in coords]
    # r = 1/12
    gens = generations(point0=point, geo_coords=coords, res=0.25)
    waves_manni = waves_manip(t_start, gens, coords, angles, waves_dwnsampled)

    if outfile:
        waves_manni.to_netcdf(f"{outfile}")

    return waves_manni



gfs = xr.open_dataset("./simulation/II/daten/env/gfs.nc")
waves = xr.open_dataset('./simulation/II/daten/env/cmems_wave.nc')
nc_mask = xr.open_dataset('./simulation/II/daten/mask.nc')

####
# wind
#
#reduce wind
red = 3
gfs["u-component_of_wind_height_above_ground"] = gfs["u-component_of_wind_height_above_ground"]/red
gfs["v-component_of_wind_height_above_ground"] = gfs["v-component_of_wind_height_above_ground"]/red

med = ulmo(gfs, nc_mask, (12.789889357194918, 37.09280205794121), (8, 39), 1, datetime.datetime(year=2023, month=10, day=31, hour=3))
indian = ulmo(med, nc_mask, (87.85821706039933, 5.609412749153263), (93, 5), 2, datetime.datetime(year=2023, month=10, day=28, hour=12))
npazific = ulmo(indian, nc_mask, (-127.62806387974446, 39.301657626529675), (-137, 50), 3, datetime.datetime(year=2023, month=10, day=28, hour=12), outfile="./simulation/II/daten/wind_mani.nc")


####
# waves
#
w = waves.coarsen(latitude=3, longitude=3, boundary='pad', coord_func='min').mean()
lo = np.array([-180 + 0.25 * i for i in range(1440)])
la = np.array([-80 + 0.25 * i for i in range(681)])
waves_dwnsampled = w.assign_coords(longitude=lo, latitude=la)


med = ulmo_wave(waves_dwnsampled, nc_mask, (12.789889357194918, 37.09280205794121), (8, 39), 1, datetime.datetime(year=2023, month=10, day=31, hour=3))
indian = ulmo_wave(med, nc_mask, (87.85821706039933, 5.609412749153263), (93, 5), 2, datetime.datetime(year=2023, month=10, day=28, hour=12))
npazific = ulmo_wave(indian, nc_mask, (-127.62806387974446, 39.301657626529675), (-137, 50), 3, datetime.datetime(year=2023, month=10, day=28, hour=12), outfile="./simulation/II/daten/waves_mani.nc")

















test = xr.open_dataset('./simulation/II/daten/env/bbox/bbox_med_gfs.nc')
mask = xr.open_dataset('./simulation/II/daten/mask.nc')
m = mask.where(mask.__xarray_dataarray_variable__ == 1, drop=True)

med = ulmo(test, mask, (12.789889357194918, 37.09280205794121), (8, 39), 1, datetime.datetime(year=2023, month=10, day=31, hour=3))