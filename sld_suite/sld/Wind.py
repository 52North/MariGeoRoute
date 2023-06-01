class Windbarbs:
    layerName = 'wind_world'
    layerStyle = 'wind_spd_dir'
    scale = 0.05
    u = 'u'
    v = 'v'
    barbStroke = '#676b70'
    barbStrokeWidth = 3
    # maybe tie bar-and cricleSize together eg cS = round(bS/10)
    barbSize = 50
    circleSize = 4
    circleFill = '#000000'

    _vals = dict(
        layerName=layerName,
        layerStyle=layerStyle,
        scale=scale,
        u=u,
        v=v,
        barbStroke=barbStroke,
        barbStrokeWidth=barbStrokeWidth,
        barbSize=barbSize,
        circleSize=circleSize,
        circleFill=circleFill
    )

    def initvals(self):
        print(self._vals)
        return (self._vals)

    def createSld(self):
        barbString = f"""sqrt(({self.u} * {self.u}) + {self.v} * {self.v}))"""
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
            <ogc:Function name="parameter">
              <ogc:Literal>emisphere</ogc:Literal>
              <ogc:Literal>True</ogc:Literal>
            </ogc:Function>
          </ogc:Function>
        </Transformation>
        <Rule>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>
                windbarbs://default(${barbString})[m/s]               
                </WellKnownName>

                <Stroke>
                  <CssParameter name="stroke">{self.barbStroke}</CssParameter>
                  <CssParameter name="stroke-width">{self.barbStrokeWidth}</CssParameter>
                </Stroke>

              </Mark>
              <Size>{self.barbSize}</Size>
              <Rotation>
                <ogc:Add>
                  <ogc:Function name="toDegrees">
                    <ogc:Function name="atan2">
                      <ogc:PropertyName>{self.u}</ogc:PropertyName>
                      <ogc:PropertyName>{self.v}</ogc:PropertyName>
                    </ogc:Function>
                  </ogc:Function>
                  <ogc:Literal>180</ogc:Literal>
                </ogc:Add>
              </Rotation>
            </Graphic>
          </PointSymbolizer>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">
                    <ogc:Literal>{self.circleFill}</ogc:Literal>
                  </CssParameter>
                </Fill>
              </Mark>
              <Size>4</Size>
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
