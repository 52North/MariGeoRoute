from .Class import BaseSLD


class Currents(BaseSLD):
    layer_name = 'currents_world'
    style_name = 'currents_dir'
    scale = 0.01
    u = 'uo'
    v = 'vo'
    # needed for largenumber-nan (-9999)
    filter_cut_off = 2.5
    # len colors has to be 1 bigger than len nums
    cat_nums = [
        0.5,
        0.75,
        1,
        1.25,
        1.5,
        1.75,
        2,
        2.5
    ]
    cat_colors = [
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
    stroke_width = 0.6
    stroke_col = '#ffffff'
    mark_size = 25
    _vals = dict(layer_name=layer_name,
                 style_name=style_name,
                 scale=scale,
                 u=u,
                 v=v,
                 filter_cut_off=filter_cut_off,
                 cat_nums=cat_nums,
                 cat_colors=cat_colors,
                 stroke_width=stroke_width,
                 stroke_col=stroke_col,
                 mark_size=mark_size)

    @staticmethod
    def categorize(cat_nums, cat_colors):
        res = [f"<ogc:Literal>{x}</ogc:Literal>" for y in zip(cat_colors, cat_nums) for x in y] + [
            f"<ogc:Literal>{cat_colors[-1]}</ogc:Literal>"]
        return "\n".join(res)

    def create_sld(self):
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
                <Title>{self.style_name}</Title>
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
                      <ogc:Literal>{self.filter_cut_off}</ogc:Literal>
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
                             {self.categorize(self.cat_nums, self.cat_colors)}
                            </ogc:Function >

                          </CssParameter>
                        </Fill>
                        <Stroke>
                          <CssParameter name="stroke-width">{self.stroke_width}</CssParameter>
                          <CssParameter name="stroke">{self.stroke_col}</CssParameter>
                        </Stroke>
                      </Mark>
                      <Size>{self.mark_size}</Size>
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