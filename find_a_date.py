import csv
from define_filters import DATE_CAT_IDS, defineFilters
from src.breed_choices import BreedChoices
from src.cat_cache import *
from src.fetch_cats import *
from src.match_cats_filters import *
from src.question_choices import *
from src.sort_cats import sortCats
from src.users import Users


def getCatData(id: str) -> CatData:
    with requests.Session() as session:
        login(session)
        return fillInCat(catId=id, session=session)


def convertCatDataListToCsvRows(catDataList: list[CatData]) -> list[list]:
    return list(map(lambda catData: catData.convertToCsvRow(), catDataList))


def addFiltersBasedOnCat(filters: MatchCatsFilters, cat: CatData):
    if cat.gender == Gender.FEMALE:
        filters.gender = Gender.MALE
        filters.saleOrStud = SaleOrStud.SALE_OR_STUD
    elif cat.gender == Gender.MALE:
        filters.gender = Gender.FEMALE
        filters.saleOrStud = SaleOrStud.SALE


def getPotentialOffspring(cat: CatData, allCats: list[CatData]):
    def avg(x, y):
        return (x + y) / 2

    for i in range(0, len(allCats)):
        offspring = allCats[i]
        # Get averages of traits
        offspring.bodyType = avg(cat.bodyType, offspring.bodyType)
        offspring.bodySize = avg(cat.bodySize, offspring.bodySize)
        offspring.headShape = avg(cat.headShape, offspring.headShape)
        offspring.earSize = avg(cat.earSize, offspring.earSize)
        offspring.noseLength = avg(cat.noseLength, offspring.noseLength)
        offspring.eyeShape = avg(cat.eyeShape, offspring.eyeShape)
        allCats[i] = offspring
    return allCats


def findADateForKittums(filters: MatchCatsFilters, cat: CatData, outputDirectory: str, filePath: str):
    try:
        createDirectory(outputDirectory)
        with open(filePath, 'w', encoding='UTF8', newline='') as f:
            addFiltersBasedOnCat(filters, cat)
            allCats = fetchCats(filters)
            potentialOffspring = getPotentialOffspring(cat, allCats)
            for catData in potentialOffspring:
                catData.scoreCat(filters)
            sortedCats = sortCats(potentialOffspring, filters)

            writer = csv.writer(f)
            writer.writerow(CatData.getCsvHeader())
            writer.writerows(convertCatDataListToCsvRows(sortedCats))

        print(f'allCats length = {len(allCats)}')
    except PermissionError as e:
        print(
            f'\nError: Please close {filePath} before running this program.')
        return False
    return True

# ------------------------------------------------------------------------


def main(catId: str):
    filters = defineFilters()
    # print(f'filters = {filters}')

    cat = getCatData(catId)
    print(f'Finding a date for cat {cat.name} (#{catId})...\n')

    filteredCatName = cat.name.translate({ord(c): None for c in '!<>@#$|#/*§'})
    OUTPUT_FILE_NAME = f'{filters.filterName}_matches_for_(#{cat.id})_{filteredCatName}.csv'
    OUTPUT_DIRECTORY = 'O_dates'
    FILE_PATH = f'{OUTPUT_DIRECTORY}/{OUTPUT_FILE_NAME}'

    success = findADateForKittums(
        filters, cat, outputDirectory=OUTPUT_DIRECTORY, filePath=FILE_PATH)
    if success:
        print(f'\nFinished successfully.')


for id in DATE_CAT_IDS:
    print(f'main(id) = {id}')
    main(id)
