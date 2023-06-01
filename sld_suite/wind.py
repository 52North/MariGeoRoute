from sld import Windbarbs

barb = Windbarbs()
barb.u = 'u-component_of_wind_height_above_ground'
barb.v = 'v-component_of_wind_height_above_ground'

barb.writeSld()
