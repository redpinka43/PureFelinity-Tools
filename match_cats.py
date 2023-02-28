import csv
from define_filters import defineFilters
from src.breed_choices import BreedChoices
from src.cat_cache import *
from src.fetch_cats import *
from src.match_cats_filters import *
from src.question_choices import *
from src.sort_cats import sortCats


def askForBreedName() -> MatchCatsFilters:
    breedInput = getChoiceInput(
        "Is there a breed from the following you'd like to match? If not, enter nothing.", BreedChoices)
    return breedInput


def haveUserDescribeBreed() -> MatchCatsFilters:
    return MatchCatsFilters()


def convertCatDataListToCsvRows(catDataList: list[CatData]) -> list[list]:
    return list(map(lambda catData: catData.convertToCsvRow(), catDataList))


def matchCatsAndOutputToFile(filters: MatchCatsFilters):
    try:
        createDirectory(OUTPUT_DIRECTORY)
        with open(FILE_PATH, 'w', encoding='UTF8', newline='') as f:
            allCats = fetchCats(filters)
            sortedCats = sortCats(allCats, filters)

            writer = csv.writer(f)
            writer.writerow(CatData.getCsvHeader())
            writer.writerows(convertCatDataListToCsvRows(sortedCats))

        print(f'allCats length = {len(allCats)}')
    except PermissionError as e:
        print(
            f'\nError: Please close {FILE_PATH} before running this program.')
        return False
    return True

# ---------------------------------------------------------------------

# filters = askForBreedName()
# if not filters:
#     filters = haveUserDescribeBreed()


print('Matching cats...\n')

filters = defineFilters()
filters.saleOrStud = SaleOrStud.SALE
filters.gender = Gender.FEMALE


# print(f'filters = {filters}')


OUTPUT_FILE_NAME = f'{filters.filterName}_{filters.gender.name.lower()}_matches.csv'
OUTPUT_DIRECTORY = 'O_breedMatches'
FILE_PATH = f'{OUTPUT_DIRECTORY}/{OUTPUT_FILE_NAME}'

success = matchCatsAndOutputToFile(filters)
if success:
    print(f'\nFinished successfully.')
