import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# DPI properties
DPI = 96

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
#SECRET_KEY = 'my precious'

# Defaults - self-explanatory
DEFAULT_MAP = [30, 0, 45, 40] #[58.1, 15.0, 68.7, 30.6] #[30, 0, 45, 40] 50, 0, 82, 90    55.0, 4.6, 67.3, 41.5 54.2, 12.5, 67.3, 41.5
DEFAULT_ROUTE = [43.5,7.2, 33.8,35.5]# 37.0, 10.6,39.4,19.8 ]35.4, 31.7[59.1, 21.7,62.0, 18.6 ] #75.8, 17.2, 76.4,60.9    58.5, 17.1, 60.2, 28.3  62.7, 18.6, 55.9, 15.3
DEFAULT_BOAT = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/polar-ITA70.csv'  #contains some boat specifics
DEFAULT_GFS_DATETIME = '2020111607'
DEFAULT_GFS_HOUR = '06'
DEFAULT_GFS_FCST = '000'
DEFAULT_GFS_RESOLUTION = '1p00'
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/20205150000_split13.grb'
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/2019122212f000'
DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/20205150000_split13.nc'
DEFAULT_GFS_MODEL = '2020111600'

# Isochrone routing parameters
ROUTER_HDGS_SEGMENTS = 180              #number of heading segments in the range of -180° to 180°
ROUTER_HDGS_INCREMENTS_DEG = 1
ISOCHRONE_EXPECTED_SPEED_KTS = 8
ISOCHRONE_PRUNE_SECTOR_DEG_HALF = 90    #angular range of azimuth that is considered for pruning (only one half)
ISOCHRONE_PRUNE_SEGMENTS = 180          #number of azimuth bins that are used for pruning
