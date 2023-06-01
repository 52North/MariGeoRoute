class Class:
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
        return

    def printSld(self):
        print(self.createSld())

    def writeSld(self, outfile=None):
        sld = self.createSld()

        with open(f'./xml/{outfile or self.layerName}.xml', 'w+') as file:
            file.write(sld)
