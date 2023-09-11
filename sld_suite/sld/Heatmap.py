from .Class import BaseSLD


class Heatmap(BaseSLD):
    def __init__(self, layer_name, style_name, cat_nums, cat_colors):
        self.layer_name = layer_name
        self.style_name = style_name
        self.cat_nums = cat_nums
        self.cat_colors = cat_colors
        self._vals = dict(
            layer_name=layer_name,
            style_name=style_name,
            cat_nums=cat_nums,
            cat_colors=cat_colors
        )

    @staticmethod
    def categorize(cat_colors, cat_nums):
        res = [f"""<ColorMapEntry color = '{col}' quantity = '{cat_nums[i]}'/>""" for i, col in enumerate(cat_colors)]
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
        
                <Rule>
                    <RasterSymbolizer>
                        <ColorMap extended = 'true'>
                    {self.categorize(self.cat_colors, self.cat_nums)}
                        </ColorMap>
                    </RasterSymbolizer>
                </Rule>
              </FeatureTypeStyle>
            </UserStyle>
          </NamedLayer>
        </StyledLayerDescriptor>   
        """)