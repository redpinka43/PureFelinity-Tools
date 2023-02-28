from src.cat_coat_data import CatCoatData
from src.util import stringifyAttributes
from src.enums import *


class MatchCatsFilters:
    def __init__(self, bodyType=None):
        self.filterName = None

        self.bodyType = bodyType
        self.gender = Gender.EITHER
        self.saleOrStud = SaleOrStud.SALE_OR_STUD
        self.minAge = None
        self.maxAge = None
        self.maxSalePrice = None
        self.maxStudFee = None
        self.maxMoodDeviation = None

        self.bodyType = None
        self.bodySize = None
        self.headShape = None
        self.earSize = None
        self.earCurl = None
        self.noseLength = None
        self.eyeShape = None
        self.eyeColor = None
        self.tail = None
        self.legs = None
        self.coat = CatCoatData()

        self.fromCacheOnly = False
        self.additionalOwnerIds = []
        self.useOnlyOwnerIds = []

    def __str__(self):
        return stringifyAttributes(self)
