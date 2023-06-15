# sld_suite

## structure

Classes are defined in ```/sld/```. <br>
There are multiple for each type of SLD. <br>
The SLD is defined within the Classes and is what separates Classes from each other.

The Files in the root directory, except for ``main.py``, are used to call said Classes and change the variables of the
SLDs.

``main.py`` is used to call all of these scripts and offers a function to ``put`` these styles on your geoserver

## how to use

- if you want to make changes to the structure of a SLD, do it in the ```/sld/``` subfolder in its respective Class or
  create a new one
- if you want to make changes to the variables (e.g. Colors and ValueRanges) of a SLD, do it in the files in the root
  directory
  <br> if you created a new Class import it somewhere here, or create a new file
- use ``python main.py`` to create all SLDs at once and the function to ``put`` the styles to your GeoServer
  <br> run `python main.py --help` to see how to use the tool (supported cli parameters, default values, etc.)

## ToDos:

- wave_dir_light_mode/wave_dir_dark_mode style: rename band to "Mean wave direction from (Mdir)" in geoserver layer
- pressure_heatmap style: set lower boundary to zero (or very small)
- check existing styles before doing POST request
