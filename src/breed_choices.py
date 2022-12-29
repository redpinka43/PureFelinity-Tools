from src.match_cats_filters import *


class BreedChoices:
    def blueOcean():
        filters = MatchCatsFilters()
        filters.filterName = 'BlueOcean'
        filters.bodyType = 5
        filters.bodySize = 17
        filters.headShape = 5
        filters.earSize = 5
        filters.earCurl = 'straight'
        filters.noseLength = 15
        filters.eyeShape = 10
        filters.tail = 'normal'
        filters.legs = 'normal'
        filters.coat = CatCoatData()
        filters.coat.length = 'longhair'
        filters.coat.baseColor = 'blue'
        return filters

    def celticFrost():
        filters = MatchCatsFilters()
        filters.filterName = 'CelticFrost'
        filters.bodyType = 10
        filters.bodySize = 17
        filters.headShape = 13
        filters.earSize = 15
        filters.earCurl = 'straight'
        filters.noseLength = 19
        filters.eyeShape = 19
        filters.eyeColor = 'blue'
        filters.tail = 'normal'
        filters.legs = 'normal'
        filters.coat = CatCoatData()
        filters.coat.length = 'shorthair'
        filters.coat.albino = 'any'
        return filters

    def chumbles():
        filters = MatchCatsFilters()
        filters.filterName = 'Chumbles'
        filters.bodyType = 9
        filters.bodySize = 16
        filters.headShape = 1
        filters.earSize = 2
        filters.earCurl = 'straight'
        filters.noseLength = 8
        filters.eyeShape = 1
        filters.eyeColor = 'blue'
        filters.tail = 'normal'
        filters.legs = 'normal'
        filters.coat = CatCoatData()
        filters.coat.length = 'shorthair'
        return filters

    def orientalStageDragon():
        filters = MatchCatsFilters()
        filters.filterName = 'OrientalStageDragon'
        filters.bodyType = 7
        filters.bodySize = 3
        filters.headShape = 2
        filters.earSize = 11
        filters.noseLength = 3
        filters.eyeShape = 15
        filters.coat = CatCoatData()
        return filters

    def palePanther():
        filters = MatchCatsFilters()
        filters.filterName = 'PalePanther'
        filters.bodyType = 15
        filters.bodySize = 10
        filters.headShape = 9
        filters.earSize = 16
        filters.earCurl = 'straight'
        filters.noseLength = 19
        filters.eyeShape = 3
        filters.eyeColor = 'blue'
        filters.tail = 'normal'
        filters.legs = 'normal'
        filters.coat = CatCoatData()
        filters.coat.length = 'shorthair'
        filters.coat.baseColor = 'white'
        filters.coat.rufused = True
        return filters

    def soluciamSilk():
        filters = MatchCatsFilters()
        filters.filterName = 'SoluciamSilk'
        filters.bodyType = 12
        filters.bodySize = 17
        filters.headShape = 12
        filters.earSize = 15
        filters.earCurl = 'straight'
        filters.noseLength = 19
        filters.eyeShape = 18
        filters.tail = 'normal'
        filters.legs = 'normal'
        filters.coat = CatCoatData()
        filters.coat.length = 'shorthair'
        filters.coat.texture = 'satin'
        filters.coat.smoke = True
        return filters
