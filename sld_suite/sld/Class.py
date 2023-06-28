import os

class BaseSLD:
    layerName = ''
    layerStyle = ''
    _vals = dict(

    )

    def initvals(self):
        print(self._vals)
        return (self._vals)

    @staticmethod
    def categorize(catColors, catNums):
        res = [f"""<ColorMapEntry color = {col} quantity = '{catNums[i]}'/>""" for i, col in enumerate(catColors)]
        return "\n".join(res)

    def createSld(self):
        raise NotImplementedError("This function has to be implemented by the child class!")

    def printSld(self):
        print(self.createSld())

    def writeSld(self, outfolder='./xml', outfile=None):
        sld = self.createSld()

        with open(os.path.join(outfolder, f'{outfile or self.layerName}.xml'), 'w+') as file:
            file.write(sld)
