class Heatmap:
    def __init__(self, layerName, styleName, catNums, catColors):
        self.layerName = layerName
        self.styleName = styleName
        self.catNums = catNums
        self.catColors = catColors

    def initvals(self, layerName, styleName, catNums, catColors):
        _vals = dict(
            layerName=layerName,
            styleName=styleName,
            catNums=catNums,
            catColors=catColors
        )
        print(_vals)
        return (_vals)

    @staticmethod
    def categorize(catColors, catNums):
        res = [f"""<ColorMapEntry color = '{col}' quantity = '{catNums[i]}'/>""" for i, col in enumerate(catColors)]
        return "\n".join(res)

    def createSld(self):
        return (f"""<?xml version="1.0" encoding="UTF-8"?>
        <StyledLayerDescriptor xmlns="http://www.opengis.net/sld"
          xmlns:ogc="http://www.opengis.net/ogc"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sld
         http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd" version="1.0.0">
          <NamedLayer>
            <Name>{self.layerName}</Name>
            <UserStyle>
              <FeatureTypeStyle>
                <Title>{self.styleName}</Title>
        
                <Rule>
                    <RasterSymbolizer>
                        <ColorMap extended = 'true'>
                    {self.categorize(self.catColors, self.catNums)}
                        </ColorMap>
                    </RasterSymbolizer>
                </Rule>
              </FeatureTypeStyle>
            </UserStyle>
          </NamedLayer>
        </StyledLayerDescriptor>   
        """)

    def printSld(self):
        print(self.createSld())

    def writeSld(self, outfile=None):
        sld = self.createSld()

        with open(f'./xml/{outfile or self.layerName}.xml', 'w+') as file:
            file.write(sld)
