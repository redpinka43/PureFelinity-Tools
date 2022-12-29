from bs4 import element, ResultSet

from src.match_cats_filters import *
from src.util import stringifyAttributes
from src.match_cats_filters import *

BID_SALE_PRICE = 999999999


def getGenderFromString(string):
    if string == 'female (n)':
        return Gender.FEMALE_NEUTERED
    if string == 'female (p)':
        return Gender.FEMALE_PREGNANT
    if string == 'male (n)':
        return Gender.MALE_NEUTERED
    return Gender(string)


class CatSearchResultData:
    def __init__(self):
        self.id = None
        self.gender = Gender.EITHER
        self.age = None
        self.salePrice = None
        self.studFee = None

    def __str__(self):
        return stringifyAttributes(self)

    def getCatIdFromNameCellText(self, text: str):
        # Example of a text we want to
        # ﴾Chant﴿ Idle&#039;s Hope </A> (#2007612)
        words = text.split()
        number = words[-1]
        number = number.strip('()#')
        return number

    def initWithSearchResultHtmlRow(self, html: element.Tag):
        cellsHtml = html.find_all('td')
        cells = list(map(lambda cellHtml: cellHtml.get_text(), cellsHtml))

        if len(cells) != 8:
            raise ValueError(
                f"Expected number of cells in search table to be 8. Received {len(cells)}")

        self.id = self.getCatIdFromNameCellText(cells[0])

        self.gender = getGenderFromString(cells[4].strip())

        self.age = int(cells[5])
        self.salePrice = int(cells[6])
        self.studFee = int(cells[7])

    def matchesFilter(self, filters: MatchCatsFilters, ignorePrice=False):
        # gender
        if self.gender == Gender.FEMALE_NEUTERED:
            if filters.gender and filters.gender != Gender.FEMALE_NEUTERED:
                return False
        if self.gender == Gender.FEMALE_PREGNANT:
            if filters.gender and filters.gender != Gender.FEMALE_PREGNANT:
                return False
        if self.gender == Gender.MALE_NEUTERED:
            if filters.gender and filters.gender != Gender.MALE_NEUTERED:
                return False
        if filters.gender and filters.gender != Gender.EITHER:
            if filters.gender != self.gender:
                return False

        # age
        if filters.maxAge and self.age > filters.maxAge:
            return False
        if filters.minAge and self.age < filters.minAge:
            return False

        # no bid
        if self.salePrice == BID_SALE_PRICE:
            return False

        # If we don't care about price (like with owned cats), return at this point
        if ignorePrice:
            return True

        # price
        exceedsSalePrice = (self.salePrice > 0) and filters.maxSalePrice and (
            filters.maxSalePrice < self.salePrice)
        exceedsStudFee = (self.studFee > 0) and filters.maxStudFee and (
            filters.maxStudFee < self.studFee)

        match filters.saleOrStud:
            case SaleOrStud.SALE:
                if exceedsSalePrice:
                    return False
            case SaleOrStud.STUD:
                if exceedsStudFee:
                    return False
            case SaleOrStud.SALE_OR_STUD:
                if exceedsSalePrice and exceedsStudFee:
                    return False
        return True


def convertHtmlRowsToCatSearchResultDatas(htmlRows: ResultSet) -> list[CatSearchResultData]:
    datas = []

    row: element.Tag
    for row in htmlRows:
        data = CatSearchResultData()
        data.initWithSearchResultHtmlRow(row)
        datas.append(data)
    return datas
