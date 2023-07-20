from sld import Depth
from sld import DepthLine

lightblue = '#2494f0'
darkblue = '#014278'
landbrown = '#967444'

def create_xml(outfolder='./xml'):
    for dep in range(-30, 1):
        depth_poly = Depth()
        depth_poly.depth = dep
        depth_poly.layer_name = f'depth_poly_light{dep}'
        depth_poly.fill = lightblue
        depth_poly.write_sld(outfolder=outfolder)

    for dep in range(-15, 1):
        depth_poly = Depth()
        depth_poly.depth = dep
        depth_poly.layer_name = f'depth_poly_dark{dep}'
        depth_poly.fill = darkblue
        depth_poly.write_sld(outfolder=outfolder)

    for dep in range(-1, 3):
        depth_poly = Depth()
        depth_poly.depth = dep
        depth_poly.layer_name = f'depth_poly_land{dep}'
        depth_poly.fill = landbrown
        depth_poly.write_sld(outfolder=outfolder)

    for dep in range(-30, 0):
        depth_line = DepthLine()
        depth_line.depth = dep
        depth_line.layer_name = f'depth_line{dep}'
        depth_line.write_sld(outfolder=outfolder)
