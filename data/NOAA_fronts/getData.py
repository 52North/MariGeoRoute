import os
import requests
import datetime
import geopandas as gpd

from pyproj import CRS

import re

from fiona.meta import layer_creation_options

with open('newdata.txt', 'r') as fronts:
    data = fronts.read()

lines = data.split('\n')

keys = ['VALID', 'HIGHS', 'LOWS', 'TROF', 'WARM', 'COLD', 'STNRY', 'OCFNT']



def joinLines(lines, keys):
    #get all lines that start with keys
    linestarts = [[i, l] for i, l in enumerate(lines) for k in keys if l.startswith(k)]
    indexes = [i[0] for i in linestarts]
    length = len(indexes)
    erg = []
    ind=[]

    #check if element is oneliner or has newlines
    for i in range(len(linestarts)-1):
        first=linestarts[i][0]
        check=linestarts[i+1][0]
        if first is not check-1:
          erg.append((first, check))

    for e in erg:
        for ls in  linestarts:
            if e[0] is ls[0]:
                ls[1]= ' '.join(lines[e[0]:e[1]])

    #join lines for newliners
    jL=[''.join(lines[i[0]:i[1]]) for i in erg]


    return([l[1] for l in linestarts])

data = joinLines(lines, keys)

def getCoords(s):
    lat = int(s[:3])/10
    lon = int(s[3:])/10
    return(dict(lat=lat, lon=lon))


ocfnt_fronts = []
warm_fronts = []
cold_fronts = []
stnry_fronts = []
trof_fronts = []

for line in data:
    if line.startswith('h'):
        date = datetime.date(line.split()[1], format='D%M%H')

    if line.startswith("HIGHS"):
        print(line)
        highs_data = line.split()[1:]  # Extract the values after "HIGHS"
        # Process and store the highs_data as needed

    elif line.startswith("LOWS"):
        lows_data = line.split()[1:]  # Extract the values after "LOWS"
        # Process and store the lows_data as needed

    elif line.startswith("COLD"):
        cold_fronts.append(line.split()[1:])

    elif line.startswith("WARM"):
        warm_fronts.append(line.split()[1:])

    elif line.startswith("TROF"):
        trof_fronts.append(line.split()[1:])

    elif line.startswith("STNRY"):
        stnry_fronts.append(line.split()[1:])

    elif line.startswith("OCFNT"):
        ocfnt_fronts.append(line.split()[1:])


from shapely.geometry import LineString


def lineStrings(fronts):
    ls=[]
    for fr in fronts:
        coords = [(getCoords(st)['lon'], getCoords(st)['lat']) for st in fr]
        ls.append(LineString(coords))

    return(ls)

crs= CRS.from_epsg(4326)

cold_lines =gpd.GeoDataFrame(geometry=lineStrings(cold_fronts), crs=crs)
warm_lines =gpd.GeoDataFrame(geometry=lineStrings(warm_fronts), crs=crs)
trof_lines =gpd.GeoDataFrame(geometry=lineStrings(trof_fronts), crs=crs)
stnry_lines =gpd.GeoDataFrame(geometry=lineStrings(stnry_fronts), crs=crs)
ocfnt_lines =gpd.GeoDataFrame(geometry=lineStrings(ocfnt_fronts), crs=crs)

output_file = "new_fronts.gpkg"

cold_lines.to_file(output_file, layer='coldFront', driver='GPKG')
warm_lines.to_file(output_file, layer='warmFront', driver='GPKG')
trof_lines.to_file(output_file, layer='trofFront', driver='GPKG')
stnry_lines.to_file(output_file, layer='stnryFront', driver='GPKG')
ocfnt_lines.to_file(output_file, layer='ocfntFront', driver='GPKG')


# Create a GeoPackage file
with gpd.GeoPackage(output_file) as gpkg:
    # Save each GeoDataFrame as a separate layer in the GeoPackage
    gpkg.add_layer(cold_lines, name='coldFront')
    gpkg.add_layer(warm_lines , name='warmFront')
    gpkg.add_layer(trof_lines , name='trofFront')
    gpkg.add_layer(stnry_lines, name='strnyFront')
    gpkg.add_layer(ocfnt_lines, name='ocfntFront')

# Create a list of LineString geometries


#

# Save the GeoDataFrame to GeoPackage format
gdf.to_file(output_file, driver="GPKG")