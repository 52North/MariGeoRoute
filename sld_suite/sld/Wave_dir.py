from .Class import BaseSLD


class WaveDir(BaseSLD):
    layer_name = 'wave_dir'
    layer_style = 'wave_dir'
    scale = 0.01
    property_name = 'Mean wave direction from (Mdir)'
    fill = '#000000'
    stroke = '#000000'
    stroke_width = 0.6
    mark_size = 25

    _vals = dict(
        layer_name=layer_name,
        layer_style=layer_style,
        scale=scale,
        property_name=property_name,
        fill=fill,
        stroke=stroke,
        stroke_width=stroke_width,
        mark_size=mark_size
    )

    def create_sld(self):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <StyledLayerDescriptor xmlns="http://www.opengis.net/sld"
          xmlns:ogc="http://www.opengis.net/ogc"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sld
         http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd" version="1.0.0">
          <NamedLayer>
            <Name>{self.layer_name}</Name>
            <UserStyle>
              <FeatureTypeStyle>
                <Title>{self.layer_style}</Title>
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
                     <ogc:PropertyName>{self.property_name}</ogc:PropertyName>
                      <ogc:Literal>0</ogc:Literal>
                    </ogc:PropertyIsGreaterThan>
                    <ogc:PropertyIsLessThan>
                     <ogc:PropertyName>{self.property_name}</ogc:PropertyName>
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
                          <CssParameter name="stroke-width">{self.stroke_width}</CssParameter>
                          <CssParameter name="stroke">{self.stroke}</CssParameter>
                        </Stroke>
                      </Mark>
                      <Size>{self.mark_size}</Size>
                      <Rotation>
              
                        <ogc:PropertyName>{self.property_name}</ogc:PropertyName>
    
                      </Rotation>
                    </Graphic>
                  </PointSymbolizer>
                </Rule>
              </FeatureTypeStyle>
            </UserStyle>
          </NamedLayer>
        </StyledLayerDescriptor>
"""