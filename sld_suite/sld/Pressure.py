class Pressure:
    layerName = 'pressure_world'
    layerStyle = 'contour_mbar'
    propertyName = 'press'
    filterIntervals = 500
    lineStroke = "#000000"
    lineStrokeWidth = 1
    fontFamily = 'Arial'
    fontFamilyStyle = 'Normal'
    fontFamilySize = 15
    fontFill = '#000000'
    haloRadius = 2.8
    haloFill = "#FFFFFF"
    haloFillOpacity = 1
    priority = 2000
    followLine = 'true'
    repeat = 10000
    maxDisplacement = 0
    maxAngleDelta = 50

    _vals = dict(
        layerName=layerName,
        layerStyle=layerStyle,
        propertyName=propertyName,
        filterIntervals=filterIntervals,
        lineStroke=lineStroke,
        lineStrokeWidth=lineStrokeWidth,
        fontFamily=fontFamily,
        fontFamilyStyle=fontFamilyStyle,
        fontFamilySize=fontFamilySize,
        fontFill=fontFill,
        haloRadius=haloRadius,
        haloFill=haloFill,
        haloFillOpacity=haloFillOpacity,
        priority=priority,
        followLine=followLine,
        repeat=repeat,
        maxDisplacement=maxDisplacement,
        maxAngleDelta=maxAngleDelta
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
                  <Name>rule1</Name>
                  <Title>Contour Line</Title>
                  <ogc:Filter>
                    <ogc:PropertyIsEqualTo>
                      <ogc:Function name="IEEERemainder">
                        <ogc:Function name="int2ddouble">
                          <ogc:PropertyName>{self.propertyName}</ogc:PropertyName>
                        </ogc:Function>
                        <ogc:Literal>{self.filterIntervals}</ogc:Literal>
                      </ogc:Function>
                      <ogc:Literal>0</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                  </ogc:Filter>
        
        
                  <LineSymbolizer>
                    <Stroke>
                      <CssParameter name="stroke">{self.lineStroke}</CssParameter>
                      <CssParameter name="stroke-width">{self.lineStrokeWidth}</CssParameter>
        
                    </Stroke>
                  </LineSymbolizer>
                  <TextSymbolizer>
                    <Label>
                      <ogc:Function name="numberFormat">
                        <ogc:Literal>0</ogc:Literal>
                        <ogc:Div>
                          <ogc:PropertyName>press</ogc:PropertyName>
                          <ogc:Literal> 100 </ogc:Literal>
                        </ogc:Div>
                      </ogc:Function>
        
        
        
                    </Label>
                    <Font>
                      <CssParameter name="font-family">{self.fontFamily}</CssParameter>
                      <CssParameter name="font-style">{self.fontFamilyStyle}</CssParameter>
                      <CssParameter name="font-size">{self.fontFamilySize}</CssParameter>
        
                    </Font>
                    <Halo>
                      <Radius>
                        <ogc:Literal>{self.haloRadius}</ogc:Literal>
                      </Radius>
                      <Fill>
                        <CssParameter name="fill">{self.haloFill}</CssParameter>
                        <CssParameter name="fill-opacity">{self.haloFillOpacity}</CssParameter>
                      </Fill>
                    </Halo>
                    <Fill>
                      <CssParameter name="fill">{self.fontFill}</CssParameter>
                    </Fill>
                    <Priority>{self.priority}</Priority>
                    <VendorOption name="followLine">{self.followLine}</VendorOption>
                    <VendorOption name="repeat">{self.repeat}</VendorOption>
                    <VendorOption name="maxDisplacement">{self.maxDisplacement}</VendorOption>
        
                    <VendorOption name="maxAngleDelta">{self.maxAngleDelta}</VendorOption>
                  </TextSymbolizer>
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
