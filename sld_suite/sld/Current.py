class Current:
    layerName = 'current_world'
    styleName = 'current_dir'
    scale = 0.01
    u = 'uo'
    v = 'vo'
    # needed for largenumber-nan (-9999)
    filterCutoff = 3
    # len colors has to be 1 bigger than len nums
    catNums = [
        0.5,
        0.75,
        1,
        1.25,
        1.5,
        1.75,
        2,
        2.5
    ]
    catColors = [
        '#ffffff',
        '#1ce3ed',
        '#2040f7',
        '#148818',
        '#e2f720',
        '#f7b320',
        '#f77a20',
        '#f73620',
        '#000000'
    ]
    strokeWidth = 0.6
    strokeCol = '#ffffff'
    markSize = 25
    _vals = dict(layerName=layerName,
                 styleName=styleName,
                 scale=scale,
                 u=u,
                 v=v,
                 filterCutoff=filterCutoff,
                 catNums=catNums,
                 catColors=catColors,
                 strokeWidth=strokeWidth,
                 strokeCol=strokeCol,
                 markSize=markSize)

    def initvals(self):
        print(self._vals)
        return (self._vals)

    @staticmethod
    def categorize(catNums, catColors):
        res = [f"<ogc:Literal>{x}</ogc:Literal>" for y in zip(catColors, catNums) for x in y] + [
            f"<ogc:Literal>{catColors[-1]}</ogc:Literal>"]
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
                <Transformation>
                  <ogc:Function name="ras:RasterAsPointCollection">
                    <ogc:Function name="parameter">
                      <ogc:Literal>data</ogc:Literal>
                    </ogc:Function>
                    <ogc:Function name="parameter">
                      <ogc:Literal>scale</ogc:Literal>
                      <ogc:Literal>{self.scale}</ogc:Literal>
                    </ogc:Function>
                    <ogc:Function name="parameter">
                      <ogc:Literal>emisphere</ogc:Literal>
                      <ogc:Literal>True</ogc:Literal>
                    </ogc:Function>
                  </ogc:Function>
                </Transformation>
                <Rule>

                  <ogc:Filter>
                    <ogc:PropertyIsLessThan>
                      <ogc:Function name="sqrt">
                        <ogc:Add>
                          <ogc:Mul>
                            <ogc:PropertyName>{self.u}</ogc:PropertyName>
                            <ogc:PropertyName>{self.u}</ogc:PropertyName>
                          </ogc:Mul>
                          <ogc:Mul>
                            <ogc:PropertyName>{self.v}</ogc:PropertyName>
                            <ogc:PropertyName>{self.v}</ogc:PropertyName>
                          </ogc:Mul>
                        </ogc:Add>
                      </ogc:Function>
                      <ogc:Literal>{self.filterCutoff}</ogc:Literal>
                    </ogc:PropertyIsLessThan>
                  </ogc:Filter>

                  <PointSymbolizer>
                    <Graphic>
                      <Mark>
                        <WellKnownName>
                        extshape://narrow              
                        </WellKnownName>
                        <Fill>
                          <CssParameter name ="fill">

                            <ogc:Function name ="Categorize">
                              <ogc:Function name="sqrt">
                                <ogc:Add>
                                  <ogc:Mul>
                                    <ogc:PropertyName>{self.u}</ogc:PropertyName>
                                    <ogc:PropertyName>{self.u}</ogc:PropertyName>
                                  </ogc:Mul>
                                  <ogc:Mul>
                                    <ogc:PropertyName>{self.v}</ogc:PropertyName>
                                    <ogc:PropertyName>{self.v}</ogc:PropertyName>
                                  </ogc:Mul>
                                </ogc:Add>
                              </ogc:Function>
                             {self.categorize(self.catNums, self.catColors)}
                            </ogc:Function >

                          </CssParameter>
                        </Fill>
                        <Stroke>
                          <CssParameter name="stroke-width">{self.strokeWidth}</CssParameter>
                          <CssParameter name="stroke">{self.strokeCol}</CssParameter>
                        </Stroke>
                      </Mark>
                      <Size>{self.markSize}</Size>
                      <Rotation>
                        <ogc:Function name="toDegrees">
                          <ogc:Function name="atan2">
                            <ogc:PropertyName>{self.u}</ogc:PropertyName>
                            <ogc:PropertyName>{self.v}</ogc:PropertyName>
                          </ogc:Function>
                        </ogc:Function>
                      </Rotation>
                    </Graphic>
                  </PointSymbolizer>
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
