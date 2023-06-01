class Depth:
    layerName = 'sea_depth'
    layerStyle = 'sea_depth'
    propertyName = 'z'
    depth = -15
    fill = '#0ACAB0'

    _vals = dict(
        layerName=layerName,
        layerStyle=layerStyle,
        propertyName=propertyName,
        depth=depth,
        fill=fill
    )

    def initvals(self):
        print(self._vals)
        return (self._vals)

    def createSld(self):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <StyledLayerDescriptor xmlns="http://www.opengis.net/sld"
          xmlns:ogc="http://www.opengis.net/ogc"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sld
         http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd" version="1.0.0">
          <NamedLayer>
            <Name>{self.layerName}</Name>
            <UserStyle>
              <FeatureTypeStyle>
                <Title>{self.layerStyle}</Title>
          

                
                <Rule>
                    <ogc:Filter>
                        <ogc:PropertyIsEqualTo>
                            <ogc:PropertyName>{self.propertyName}</ogc:PropertyName>
                            <ogc:Literal>{self.depth}</ogc:Literal>
                        </ogc:PropertyIsEqualTo>
                    </ogc:Filter>
                
                
                    <PolygonSymbolizer>
                        <Fill>
                          <CssParameter name="fill">{self.fill}</CssParameter>
                        </Fill>

                    </PolygonSymbolizer>
                </Rule>
              </FeatureTypeStyle>
            </UserStyle>
          </NamedLayer>
        </StyledLayerDescriptor>
                """

    def printSld(self):
        print(self.createSld())

    def writeSld(self, outfile=None):
        sld = self.createSld()

        with open(f'./xml/{outfile or self.layerName}.xml', 'w+') as file:
            file.write(sld)
