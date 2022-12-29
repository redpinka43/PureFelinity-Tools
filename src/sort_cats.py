from src.cat_data import CatData
from src.enums import SaleOrStud
from src.match_cats_filters import MatchCatsFilters


def sortCats(allCats: list[CatData], filters: MatchCatsFilters):
    def compare(cat: CatData):
        # Sale or stud
        price = min(cat.salePrice, cat.studFee)
        if filters.saleOrStud == SaleOrStud.SALE or cat.studFee == 0:
            price = cat.salePrice
        elif filters.saleOrStud == SaleOrStud.STUD or cat.salePrice == 0:
            price = cat.studFee
        return (cat.score.getTotalTraitDeviancy(), cat.score.getImperfectTraitsScore(), price, cat.getAge())

    allCats.sort(key=compare)
    return allCats
