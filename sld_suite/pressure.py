from sld import Pressure

def create_xml(outfolder='./xml'):
    press = Pressure()
    press.propertyName = 'press'
    press.writeSld(outfolder=outfolder)
