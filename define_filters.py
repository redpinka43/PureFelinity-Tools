
from src.match_cats_filters import *
from src.breed_choices import BreedChoices
from src.users import Users

NUMBER_OF_DAYS_IN_WHICH_WE_WILL_BE_BREEDING = 7     # 5 if it's a Wednesday


def defineFilters() -> MatchCatsFilters:
    filters = BreedChoices.celticFrost()

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
    2029233,
    2029230,
    2029234,
    2029231,
    2024071

]

DATE_CAT_IDS = map(lambda id: str(id).zfill(7), nonexported_date_cat_ids)
