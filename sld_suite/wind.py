from sld import Windbarbs

def create_xml(outfolder='./xml'):
    barb = Windbarbs()
    barb.u = 'u'
    barb.v = 'v'
    barb.write_sld(outfolder=outfolder)
