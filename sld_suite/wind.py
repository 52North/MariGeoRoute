from sld import Windbarbs

def create_xml(outfolder='./xml'):
    barb = Windbarbs()
    barb.u = 'u-component_of_wind_height_above_ground'
    barb.v = 'v-component_of_wind_height_above_ground'
    barb.writeSld(outfolder=outfolder)
