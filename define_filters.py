
from src.match_cats_filters import *
from src.breed_choices import BreedChoices
from src.users import Users

NUMBER_OF_DAYS_IN_WHICH_WE_WILL_BE_BREEDING = 1     # 5 if it's a Wednesday


def defineFilters() -> MatchCatsFilters:
    filters = BreedChoices.miniatureLeopard()

    filters.minAge = 9 - NUMBER_OF_DAYS_IN_WHICH_WE_WILL_BE_BREEDING
    filters.maxAge = 80 - NUMBER_OF_DAYS_IN_WHICH_WE_WILL_BE_BREEDING
    filters.maxSalePrice = 600
    filters.maxStudFee = 600
    filters.maxMoodDeviation = 9 + NUMBER_OF_DAYS_IN_WHICH_WE_WILL_BE_BREEDING

    filters.fromCacheOnly = True
    filters.additionalOwnerIds = Users.allMyUsers
    # filters.useOnlyOwnerIds = True

    return filters


nonexported_date_cat_ids = [
    2032549,
    2036409,
    2032552,
    2030844,
    2037663,
    2036406,
    2030944,
    2034244,
    2034245,
    2037661,
    2034219

]

DATE_CAT_IDS = map(lambda id: str(id).zfill(7), nonexported_date_cat_ids)
