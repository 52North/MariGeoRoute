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
