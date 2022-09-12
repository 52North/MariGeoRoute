# ISOCHRONE CODE


## Environment
### To be installed in system:-
name: windrouter
channels:
  - defaults
  - conda-forge
dependencies:
  - cartopy
  - coverage
  - flask
  - matplotlib
  - numpy
  - pip
  - pygrib
  - pyproj
  - python=3.7.7
  - scipy
  - pip:
    - geovectorslib==1.1
## Requirements
* Python 3.7+

## Instructions 
* Step-1:-First Run the isochrone.py file 
* Step-2:-Then run polars.py
* Step-3:-Then run weather.py file
* Step-4:-Then run the router.py file
* Step-5:-Then run console.py

## References
- [Henry H.T. Chen's PhD Thesis](http://resolver.tudelft.nl/uuid:a6112879-4298-40a6-91c7-d9a431a674c7)
- Modeling and Optimization Algorithms in Ship Weather Routing, doi:10.1016/j.enavi.2016.06.004
- Optimal Ship Weather Routing Using Isochrone Method on the Basis of Weather Changes, doi:10.1061/40932(246)435
- Karin, Todd. Global Land Mask. October 5, 2020. doi:10.5281/zenodo.4066722
- [GFS grib2 filter](https://nomads.ncep.noaa.gov/)
- [Boat polars - 1](https://jieter.github.io/orc-data/site/)
- [Boat polars - 2](https://l-36.com/polar_polars.php)
- https://en.wikisource.org/wiki/The_American_Practical_Navigator/Chapter_1
- https://gist.github.com/jeromer/2005586
- https://towardsdatascience.com/calculating-the-bearing-between-two-geospatial-coordinates-66203f57e4b4
- https://www.youtube.com/watch?v=DeFZ6AHtYxg
- https://www.movable-type.co.uk/scripts/latlong.html
- https://gis.stackexchange.com/questions/425515/converting-between-lat-long-azimuth-and-distance-heading
- https://geopy.readthedocs.io/en/stable/
- https://www.siranah.de/html/sail020f.html
- https://github.com/hakola/marine-traffic-modelling
- http://www.movable-type.co.uk/scripts/latlong.html?from=48.955550,-122.05169&to=48.965496,-122.072989
- https://geographiclib.sourceforge.io/html/python/code.html#geographiclib.geodesic.Geodesic.Inverse
- https://mathsathome.com/calculating-bearings/ 
