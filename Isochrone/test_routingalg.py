import pytest
import numpy as np
import xarray as xr
import datetime

import utils
from IsoBased import IsoBased
from Constraints import *

def generate_dummy_constraint_list():
    pars = ConstraintPars()
    pars.resolution = 1./10

    constraint_list = ConstraintsList(pars)
    return constraint_list

def create_dummy_ra_object():
    start = (30, 45)
    finish = (0, 20)
    date = datetime.date.today()
    prune_sector_half = 90
    nof_prune_segments = 5
    nof_hdgs_segments = 4
    hdgs_increments = 1

    ra = IsoBased(start, finish, date)
    ra.set_pruning_settings(prune_sector_half, nof_prune_segments)
    ra.set_variant_segments(nof_hdgs_segments, hdgs_increments)
    return ra
'''
    Test whether shapes of arrays are sensible after define_variants()
'''
def test_define_variants_array_shapes():
    nof_hdgs_segments = 4
    hdgs_increments = 1

    ra = create_dummy_ra_object()
    current_var = ra.get_current_azimuth()
    ra.set_variant_segments(nof_hdgs_segments, hdgs_increments)

    ra.define_variants()
    ra.print_shape()
    ra.print_ra()
    #checking 2D arrays
    assert ra.lats_per_step.shape[1] == nof_hdgs_segments+1
    assert ra.dist_per_step.shape == ra.lats_per_step.shape
    assert ra.azimuth_per_step.shape == ra.lats_per_step.shape
    assert ra.speed_per_step.shape == ra.lats_per_step.shape
    assert ra.fuel_per_step.shape == ra.lats_per_step.shape

    #checking 1D arrays
    assert ra.full_time_traveled.shape[0] == nof_hdgs_segments+1
    assert ra.full_dist_traveled.shape == ra.full_time_traveled.shape
    assert ra.time.shape == ra.full_time_traveled.shape
    assert ra.full_fuel_consumed.shape == ra.full_time_traveled.shape

'''
    test whether current_variant is correctly filled in define_variants()
'''
def test_define_variants_current_variant_filling():
    ra = create_dummy_ra_object()

    current_var = ra.get_current_azimuth()

    ra.define_variants()
    ra.print_shape()
    ra.print_ra()

    # checking current_variant
    assert ra.current_variant.shape[0] == ra.lats_per_step.shape[1]

    test_current_var = np.array([current_var+2, current_var+1, current_var, current_var-1, current_var-2])

    for i in range(0,test_current_var.shape[0]):
       assert test_current_var[i] == ra.current_variant[i]

'''
    test whether indices survive the pruning which maximise the total distance traveled
'''
def test_pruning_select_correct_idxs():
    nof_hdgs_segments = 8
    hdgs_increments = 1

    ra = create_dummy_ra_object()
    ra.set_variant_segments(nof_hdgs_segments, hdgs_increments)
    ra.define_variants()

    pruning_bins =  np.array([10,20,40,60, 80])
    ra.current_variant = np.array([15,16 ,22,23, 44,45, 71,72,74])
    ra.current_azimuth = np.array([15,16 ,22,23, 44,45, 71,72,74])
    ra.full_dist_traveled = np.array([1,5, 6,1, 2,7, 10,1,8])
    ra.full_time_traveled = np.random.rand(9)
    ra.full_fuel_consumed = np.random.rand(9)

    ra.dist_per_step = np.array([ra.full_dist_traveled])
    ra.fuel_per_step = np.array([ra.full_fuel_consumed])
    ra.azimuth_per_step = np.array([ra.current_azimuth])
    ra.speed_per_step = np.random.rand(1,9)

    cur_var_test = np.array([16, 22, 45, 71])
    cur_azi_test = np.array([16, 22, 45, 71])
    full_dist_test = np.array([5, 6, 7, 10])
    full_time_test = np.array([ra.full_time_traveled[1],ra.full_time_traveled[2],ra.full_time_traveled[5],ra.full_time_traveled[6]])
    full_fuel_test = np.array([ra.full_fuel_consumed[1],ra.full_fuel_consumed[2],ra.full_fuel_consumed[5],ra.full_fuel_consumed[6]])
    speed_ps_test = np.array([ra.speed_per_step[0,1],ra.speed_per_step[0,2],ra.speed_per_step[0,5],ra.speed_per_step[0,6]])
    lat_test = np.array([[30,30,30,30]])
    lon_test = np.array([[45,45,45,45]])
    time_test = np.array([datetime.date.today(),datetime.date.today(),datetime.date.today(),datetime.date.today()])

    ra.print_ra()
    utils.print_line()

    ra.pruning(True, pruning_bins)

    assert np.array_equal(cur_var_test,ra.current_variant)
    assert np.array_equal(cur_azi_test, ra.current_azimuth)
    assert np.array_equal(full_time_test, ra.full_time_traveled)
    assert np.array_equal(full_fuel_test, ra.full_fuel_consumed)
    assert np.array_equal(full_dist_test, ra.full_dist_traveled)

    assert np.array_equal(cur_azi_test,ra.azimuth_per_step[0])
    assert np.array_equal(full_dist_test, ra.dist_per_step[0])
    assert np.array_equal(full_fuel_test, ra.fuel_per_step[0])
    assert np.array_equal(speed_ps_test, ra.speed_per_step[0])
    assert np.array_equal(lat_test, ra.lats_per_step)
    assert np.array_equal(lon_test, ra.lons_per_step)
    assert np.array_equal(time_test, ra.time)

    #utils.print_line()
    #ra.print_ra()
'''
    test shape and content of 'move' for known distance, start and end points
'''
def test_check_bearing():
    lat_start = 51.289444
    lon_start = 6.766667
    lat_end = 60.293333
    lon_end = 5.218056
    dist_travel = 1007.091*1000
    az = 355.113

    ra = create_dummy_ra_object()
    ra.lats_per_step = np.array([[lat_start, lat_start, lat_start, lat_start]])
    ra.lons_per_step = np.array([[lon_start, lon_start, lon_start, lon_start]])
    ra.current_variant = np.array([az,az,az,az])

    dist = np.array([dist_travel, dist_travel, dist_travel, dist_travel])

    lats_test = np.array([
        [lat_end, lat_end, lat_end, lat_end],
        [lat_start, lat_start, lat_start, lat_start]]
    )
    lons_test = np.array([
        [lon_end, lon_end, lon_end, lon_end],
        [lon_start, lon_start, lon_start, lon_start]]
    )

    ra.print_ra()
    move = ra.check_bearing(dist)

    #print('lats_test[0]', lats_test[0])
    #print('lons_test[0]', lons_test[0])
    assert np.allclose(lats_test[0], move['lat2'], 0.01)
    assert np.allclose(lons_test[0], move['lon2'], 0.01)

'''
    test results for elements of is_constrained
'''
def test_check_constraints_land_crossing():
    move = {'lat2' : np.array([52.70, 53.55]),  #1st point: land crossing (failure), 2nd point: no land crossing(success)
            'lon2' : np.array([4.04, 5.45])}

    ra = create_dummy_ra_object()
    ra.lats_per_step = np.array([[52.76, 53.45]])
    ra.lons_per_step = np.array([[5.40, 3.72]])

    land_crossing = LandCrossing()
    wave_height = WaveHeight()
    wave_height.current_wave_height = np.array([5, 5])

    #is_constrained = [False for i in range(0, lat.shape[1])]
    constraint_list = generate_dummy_constraint_list()
    constraint_list.add_neg_constraint(land_crossing)
    constraint_list.add_neg_constraint(wave_height)
    is_constrained = ra.check_constraints(move, constraint_list)
    assert is_constrained[0] == 1
    assert is_constrained[1] == 0

'''
    test whether IsoBased.update_position() updates current_azimuth, lats/lons_per_step, dist_per_step correctly
        - boat crosses land
'''
def test_update_position_fail():
    lat_start = 51.289444
    lon_start = 6.766667
    lat_end = 60.293333
    lon_end = 5.218056
    dist_travel = 1007.091*1000
    az = 355.113
    az_till_start = 330.558

    ra = create_dummy_ra_object()
    ra.lats_per_step = np.array([[lat_start,lat_start,lat_start,lat_start]])
    ra.lons_per_step = np.array([[lon_start,lon_start,lon_start,lon_start]])
    ra.azimuth_per_step = np.array([[0,0,0,0]])
    ra.dist_per_step = np.array([[0,0,0,0]])
    ra.current_variant = np.array([az,az,az,az])

    dist = np.array([dist_travel,dist_travel,dist_travel,dist_travel])

    land_crossing = LandCrossing()
    wave_height = WaveHeight()
    wave_height.current_wave_height = np.array([5, 5, 5, 5])

    # is_constrained = [False for i in range(0, lat.shape[1])]
    constraint_list = generate_dummy_constraint_list()
    constraint_list.add_neg_constraint(land_crossing)
    constraint_list.add_neg_constraint(wave_height)

    move = ra.check_bearing(dist)
    constraints = ra.check_constraints(move, constraint_list)
    ra.update_position(move, constraints, dist)

    lats_test = np.array([
        [lat_end, lat_end, lat_end, lat_end],
        [lat_start,lat_start,lat_start,lat_start]]
    )
    lons_test = np.array([
        [lon_end, lon_end, lon_end, lon_end],
        [lon_start, lon_start, lon_start, lon_start]]
    )
    dist_test = np.array([
        [dist_travel,dist_travel,dist_travel,dist_travel],
        [0, 0, 0, 0]
    ])
    az_test = np.array([
        #[az_till_start,az_till_start,az_till_start,az_till_start],
        [az,az,az,az],
        [0,0,0,0]
    ])


    assert np.allclose(lats_test, ra.lats_per_step, 0.01)
    assert np.allclose(lons_test, ra.lons_per_step, 0.01)
    assert np.allclose(ra.current_variant,np.array([az_till_start,az_till_start,az_till_start,az_till_start]), 0.1)
    assert np.array_equal(ra.dist_per_step,dist_test)
    assert np.array_equal(ra.azimuth_per_step,az_test)

    assert np.array_equal(ra.full_dist_traveled, np.array([0,0,0,0]))


'''
    test whether IsoBased.update_position() updates current_azimuth, lats/lons_per_step, dist_per_step correctly
        - no land crossing
'''
def test_update_position_success():
    lat_start = 53.55
    lon_start = 5.45
    lat_end = 53.45
    lon_end = 3.72
    dist_travel = 1007.091*1000
    az = 355.113
    az_till_start = 330.558

    ra = create_dummy_ra_object()
    ra.lats_per_step = np.array([[lat_start,lat_start,lat_start,lat_start]])
    ra.lons_per_step = np.array([[lon_start,lon_start,lon_start,lon_start]])
    ra.azimuth_per_step = np.array([[0,0,0,0]])
    ra.dist_per_step = np.array([[0,0,0,0]])
    ra.current_variant = np.array([az,az,az,az])

    dist = np.array([dist_travel,dist_travel,dist_travel,dist_travel])

    land_crossing = LandCrossing()
    wave_height = WaveHeight()
    wave_height.current_wave_height = np.array([5, 5, 5, 5])

    # is_constrained = [False for i in range(0, lat.shape[1])]
    constraint_list = generate_dummy_constraint_list()
    constraint_list.add_neg_constraint(land_crossing)
    constraint_list.add_neg_constraint(wave_height)

    move = ra.check_bearing(dist)
    constraints = ra.check_constraints(move, constraint_list)
    ra.update_position(move, constraints, dist)

    no_constraints = ra.full_dist_traveled > 0
    assert np.array_equal(no_constraints, np.array([1,1,1,1]))