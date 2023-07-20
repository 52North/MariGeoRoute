from .Class import BaseSLD


class DepthLine(BaseSLD):
    layer_name = 'sea_depth_line'
    layer_style = 'sea_depth_line'
    property_name = 'z'
    depth = -15
    stroke_width = 5

    _vals = dict(
        layer_name=layer_name,
        layer_style=layer_style,
        property_name=property_name,
        depth=depth,
        stroke_width=stroke_width
    )

    def create_sld(self):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" 
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
 xmlns="http://www.opengis.net/sld" 
 xmlns:ogc="http://www.opengis.net/ogc" 
 xmlns:xlink="http://www.w3.org/1999/xlink" 
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

  <NamedLayer>
    <Name>{self.layer_name}</Name>
    <UserStyle>  
      <Title>{self.layer_style}</Title>
      <FeatureTypeStyle>

        
        <Rule>
          <Name>rule1</Name>
          
          
          
        <ogc:Filter>
          <ogc:PropertyIsEqualTo>
            <ogc:PropertyName>{self.property_name}</ogc:PropertyName>
              <ogc:Literal>{self.depth}</ogc:Literal>
          </ogc:PropertyIsEqualTo>
        </ogc:Filter>
        
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">{self.stroke_width}</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>

                """