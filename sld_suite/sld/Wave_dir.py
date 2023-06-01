class WaveDir:
    layerName = 'wave_dir'
    layerStyle = 'wave_dir'
    scale = 0.01
    propertyName = 'Mean wave direction from (Mdir)'
    fill = '#000000'
    stroke = '#000000'
    strokeWidth = 0.6
    markSize = 25

    _vals = dict(
        layerName=layerName,
        layerStyle=layerStyle,
        scale=scale,
        propertyName=propertyName,
        fill=fill,
        stroke=stroke,
        strokeWidth=strokeWidth,
        markSize=markSize
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
                <Transformation>
                  <ogc:Function name="ras:RasterAsPointCollection">
                    <ogc:Function name="parameter">
                      <ogc:Literal>data</ogc:Literal>
                    </ogc:Function>
                    <ogc:Function name="parameter">
                      <ogc:Literal>scale</ogc:Literal>
                      <ogc:Literal>{self.scale}</ogc:Literal>
                    </ogc:Function>

                  </ogc:Function>
                </Transformation>
                <Rule>

   
                  <ogc:Filter>
                    <ogc:And>
                    <ogc:PropertyIsGreaterThan>
                     <ogc:PropertyName>{self.propertyName}</ogc:PropertyName>
                      <ogc:Literal>0</ogc:Literal>
                    </ogc:PropertyIsGreaterThan>
                    <ogc:PropertyIsLessThan>
                     <ogc:PropertyName>{self.propertyName}</ogc:PropertyName>
                      <ogc:Literal>360</ogc:Literal>
                    </ogc:PropertyIsLessThan>
                      </ogc:And>
                  </ogc:Filter>

                  <PointSymbolizer>
                    <Graphic>
                      <Mark>
                        <WellKnownName>
                        extshape://narrow              
                        </WellKnownName>
                        <Fill>
                          <CssParameter name ="fill">{self.fill}            

                          </CssParameter>
                        </Fill>
                        <Stroke>
                          <CssParameter name="stroke-width">{self.strokeWidth}</CssParameter>
                          <CssParameter name="stroke">{self.stroke}</CssParameter>
                        </Stroke>
                      </Mark>
                      <Size>{self.markSize}</Size>
                      <Rotation>
              
                        <ogc:PropertyName>{self.propertyName}</ogc:PropertyName>
    
                      </Rotation>
                    </Graphic>
                  </PointSymbolizer>
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
