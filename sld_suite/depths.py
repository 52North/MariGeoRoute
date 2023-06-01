from sld import Depth
from sld import DepthLine

lightblue = '#2494f0'
darkblue = '#014278'
landbrown = '#967444'

for dep in range(-30, 1):
    depth_poly = Depth()
    depth_poly.depth = dep
    depth_poly.layerName = f'depth_poly_light{dep}'
    depth_poly.fill = lightblue
    depth_poly.writeSld()

for dep in range(-15, 1):
    depth_poly = Depth()
    depth_poly.depth = dep
    depth_poly.layerName = f'depth_poly_dark{dep}'
    depth_poly.fill = darkblue
    depth_poly.writeSld()

for dep in range(-1, 3):
    depth_poly = Depth()
    depth_poly.depth = dep
    depth_poly.layerName = f'depth_poly_land{dep}'
    depth_poly.fill = landbrown
    depth_poly.writeSld()

for dep in range(-30, 0):
    depth_line = DepthLine()
    depth_line.depth = dep
    depth_line.layerName = f'depth_line{dep}'
    depth_line.writeSld()
