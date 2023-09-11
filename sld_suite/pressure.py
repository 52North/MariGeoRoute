from sld import Pressure

def create_xml(outfolder='./xml'):
    press = Pressure()
    press.property_name = 'press'
    press.write_sld(outfolder=outfolder)
