import os

class BaseSLD:
    layer_name = ''
    layer_style = ''
    _vals = dict(

    )

    def initvals(self):
        print(self._vals)
        return self._vals

    @staticmethod
    def categorize(cat_colors, cat_nums):
        res = [f"""<ColorMapEntry color = {col} quantity = '{cat_nums[i]}'/>""" for i, col in enumerate(cat_colors)]
        return "\n".join(res)

    def create_sld(self):
        raise NotImplementedError("This function has to be implemented by the child class!")

    def print_sld(self):
        print(self.create_sld())

    def write_sld(self, outfolder='./xml', outfile=None):
        sld = self.create_sld()

        with open(os.path.join(outfolder, f'{outfile or self.layer_name}.xml'), 'w+') as file:
            file.write(sld)
