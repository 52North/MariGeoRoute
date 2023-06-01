# sld_suite

## structure

Classes are defined in ```/sld/```. <br>
There are multiple for each type of SLD. <br>
The SLD is defined within the Classes and is what seperates Classes from eachother.

The Files in the root directory, except for ``main.py``, are used to call said Classes and change the variables of the
SLDs.

``main.py`` is used to call all of these scripts and offers a function to ``put`` these styles on your geoserver

## how to use

- if you want to make changes to the structure of a SLD, do it in the ```/sld/``` subfolder in its respective Class or
  create
  a new one
- if you want to make changes to the variables (eg. Colors and ValueRanges) of a SLD, do it in the files in the root
  directory
  <br> if you created a new Class import it somewhere here, or create a new file
- use ``main.py`` to create all SLDs at once and the function to ``put`` the styles to your geoserver
  <br> the function arguments default to the geoserver configuration on your localhost
