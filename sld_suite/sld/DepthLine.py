from .Class import BaseSLD


class DepthLine(BaseSLD):
    layerName = 'sea_depth_line'
    layerStyle = 'sea_depth_line'
    propertyName = 'z'
    depth = -15
    strokeWidth = 5

    _vals = dict(
        layerName=layerName,
        layerStyle=layerStyle,
        propertyName=propertyName,
        depth=depth,
        strokeWidth=strokeWidth
    )

    def createSld(self):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" 
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
 xmlns="http://www.opengis.net/sld" 
 xmlns:ogc="http://www.opengis.net/ogc" 
 xmlns:xlink="http://www.w3.org/1999/xlink" 
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

  <NamedLayer>
    <Name>{self.layerName}</Name>
    <UserStyle>  
      <Title>{self.layerStyle}</Title>
      <FeatureTypeStyle>

        
        <Rule>
          <Name>rule1</Name>
          
          
          
        <ogc:Filter>
          <ogc:PropertyIsEqualTo>
            <ogc:PropertyName>{self.propertyName}</ogc:PropertyName>
              <ogc:Literal>{self.depth}</ogc:Literal>
          </ogc:PropertyIsEqualTo>
        </ogc:Filter>
        
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">{self.strokeWidth}</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>

                """