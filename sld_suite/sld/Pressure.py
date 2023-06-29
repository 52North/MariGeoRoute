from .Class import BaseSLD


class Pressure(BaseSLD):
    layer_name = 'pressure_world'
    layer_style = 'contour_mbar'
    property_name = 'press'
    filter_intervals = 500
    line_stroke = "#000000"
    line_stroke_width = 1
    font_family = 'Arial'
    font_family_style = 'Normal'
    font_family_size = 15
    font_fill = '#000000'
    halo_radius = 2.8
    halo_fill = "#FFFFFF"
    halo_fill_opacity = 1
    priority = 2000
    follow_line = 'true'
    repeat = 10000
    max_displacement = 0
    max_angle_delta = 50

    _vals = dict(
        layer_name=layer_name,
        layer_style=layer_style,
        property_name=property_name,
        filter_intervals=filter_intervals,
        line_stroke=line_stroke,
        line_stroke_width=line_stroke_width,
        font_family=font_family,
        font_family_style=font_family_style,
        font_family_size=font_family_size,
        font_fill=font_fill,
        halo_radius=halo_radius,
        halo_fill=halo_fill,
        halo_fill_opacity=halo_fill_opacity,
        priority=priority,
        follow_line=follow_line,
        repeat=repeat,
        max_displacement=max_displacement,
        max_angle_delta=max_angle_delta
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
        
                <Rule>
                  <Name>rule1</Name>
                  <Title>Contour Line</Title>
                  <ogc:Filter>
                    <ogc:PropertyIsEqualTo>
                      <ogc:Function name="IEEERemainder">
                        <ogc:Function name="int2ddouble">
                          <ogc:PropertyName>{self.property_name}</ogc:PropertyName>
                        </ogc:Function>
                        <ogc:Literal>{self.filter_intervals}</ogc:Literal>
                      </ogc:Function>
                      <ogc:Literal>0</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                  </ogc:Filter>
        
        
                  <LineSymbolizer>
                    <Stroke>
                      <CssParameter name="stroke">{self.line_stroke}</CssParameter>
                      <CssParameter name="stroke-width">{self.line_stroke_width}</CssParameter>
        
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
                      <CssParameter name="font-family">{self.font_family}</CssParameter>
                      <CssParameter name="font-style">{self.font_family_style}</CssParameter>
                      <CssParameter name="font-size">{self.font_family_size}</CssParameter>
        
                    </Font>
                    <Halo>
                      <Radius>
                        <ogc:Literal>{self.halo_radius}</ogc:Literal>
                      </Radius>
                      <Fill>
                        <CssParameter name="fill">{self.halo_fill}</CssParameter>
                        <CssParameter name="fill-opacity">{self.halo_fill_opacity}</CssParameter>
                      </Fill>
                    </Halo>
                    <Fill>
                      <CssParameter name="fill">{self.font_fill}</CssParameter>
                    </Fill>
                    <Priority>{self.priority}</Priority>
                    <VendorOption name="followLine">{self.follow_line}</VendorOption>
                    <VendorOption name="repeat">{self.repeat}</VendorOption>
                    <VendorOption name="maxDisplacement">{self.max_displacement}</VendorOption>
        
                    <VendorOption name="maxAngleDelta">{self.max_angle_delta}</VendorOption>
                  </TextSymbolizer>
                </Rule>
        
              </FeatureTypeStyle>
            </UserStyle>
          </NamedLayer>
        </StyledLayerDescriptor>
        """