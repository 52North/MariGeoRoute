import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# DPI properties
DPI = 96

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
# SECRET_KEY = 'my precious'

# Defaults - self-explanatory
DEFAULT_MAP = [30, 0, 45, 40]
DEFAULT_ROUTE = [43.5,7.2, 33.8,35.5]
TIME_FORECAST = 10     # [hours]
DELTA_TIME_FORECAST = 3600 # [seconds]
#DEFAULT_GFS_DATETIME = '2020111600' #NCEP
DEFAULT_GFS_DATETIME = '2019060211' #CMEMS
DEFAULT_GFS_HOUR = '06'
DEFAULT_GFS_FCST = '000'
DEFAULT_GFS_RESOLUTION = '1p00'
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/20205150000_split13.grb'
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/2019122212f000'
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/20205150000_split13.nc'
DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/20221110/45d7b138-61a8-11ed-bdaf-0242ac120003.nc'
DEFAULT_GFS_MODEL = '2020111600'

# Isochrone routing parameters
ROUTER_HDGS_SEGMENTS =  180 #number of heading segments in the range of -180° to 180°
ROUTER_HDGS_INCREMENTS_DEG = 1
ROUTER_RPM_SEGMENTS = 20
ROUTER_RPM_INCREMENTS_DEG = 1
ISOCHRONE_EXPECTED_SPEED_KTS = 8
ISOCHRONE_PRUNE_SECTOR_DEG_HALF = 90    #angular range of azimuth that is considered for pruning (only one half)
ISOCHRONE_PRUNE_SEGMENTS = 180          #number of azimuth bins that are used for pruning

# boat settings
DEFAULT_BOAT = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/polar-ITA70.csv'  #contains some boat specifics
