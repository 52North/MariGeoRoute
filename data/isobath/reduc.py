import xarray as xr
import numpy as np
import os

def get_scale_and_offset(minV, maxV, n):
    scale=(maxV - minV)/(2**n-1)
    offset=minV + 2**(n-1) * scale
    return scale.values.tolist(), offset.values.tolist()


#https://www.ncei.noaa.gov/products/etopo-global-relief-model
file='ETOPO_2022_v1_30s_N90W180_bed.nc'

data=xr.open_dataset(file)
data_2=data.where(data.z<2)

#32GB RAM sind nicht genug
del data

data_30_2=data_2.where(data_2.z>-30)

#32GB RAM sind nicht genug
del data_2


scale, offset = get_scale_and_offset(np.min(data_30_2.z), np.max(data_30_2.z), 8)


fval = (-30 - offset)/scale
#fval = np.NaN

encoding = {'z': 
            {'dtype': "int8",
             'scale_factor': scale,
             'add_offset': offset,
             '_FillValue': fval}
            }

data_30_2 = data_30_2.drop_vars('crs')
data_30_2.to_netcdf('d30_2.nc', encoding=encoding, engine='h5netcdf')

del data_30_2
os.system(f"""
gdal_contour -a z -b 1 -fl -30 -29 -28 -27 -26 -25 -24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13 -12 -11 -10 -9 -8 -7 -6 -5 -4 -3 -2 -1 0 1 2 -f "GPKG" ETOPO_2022_v1_30s_N90W180_bed.nc isobathen.gpkg
""")

