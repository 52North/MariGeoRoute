from .Class import BaseSLD


class Windbarbs(BaseSLD):
    layer_name = 'wind_world'
    layer_style = 'wind_spd_dir'
    scale = 0.005
    u = 'u'
    v = 'v'
    barb_stroke = '#676b70'
    barb_stroke_width = 3
    # maybe tie barb_size cand circle_size together e.g. circle_size = round(barb_size/10)
    barb_size = 50
    circle_size = 4
    circle_fill = '#000000'

    _vals = dict(
        layer_name=layer_name,
        layer_style=layer_style,
        scale=scale,
        u=u,
        v=v,
        barb_stroke=barb_stroke,
        barb_stroke_width=barb_stroke_width,
        barb_size=barb_size,
        circle_size=circle_size,
        circle_fill=circle_fill
    )

    def create_sld(self):
        barb_string = f"""{{sqrt(({self.u} * {self.u}) + ({self.v} * {self.v}))}}"""
        return (f"""<?xml version="1.0" encoding="UTF-8"?>
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
                windbarbs://default(${barb_string})[m/s]               
                </WellKnownName>

                <Stroke>
                  <CssParameter name="stroke">{self.barb_stroke}</CssParameter>
                  <CssParameter name="stroke-width">{self.barb_stroke_width}</CssParameter>
                </Stroke>

              </Mark>
              <Size>{self.barb_size}</Size>
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
                    <ogc:Literal>{self.circle_fill}</ogc:Literal>
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