import requests
from src.cat_cache import loadCatCache, saveCatCache
from src.cat_data import AGE_WHEN_CATS_START_BREEDING, AGE_WHEN_FEMALE_CANT_BREED_ANYMORE, CatData
from src.fetch_cats_payload_data import *
from src.get_cat_ids_from_owners_page import getCatIdsFromOwnersList
from src.get_cat_ids_from_search_results import getCatIdsFromSearchResults
from src.match_cats_filters import MatchCatsFilters
from src.mock_data import *
from src.cat_search_result_data import *


from src.util import USE_MOCK_DATA, sleepForABit, tryUntilSucceed


def login(session):
    try:
        response = session.post(LOGIN_URL, data=loginPayload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    print('Successfully logged in.')


def getCatIdsToFetch(filters: MatchCatsFilters, session) -> list[str]:
    catIds = getCatIdsFromOwnersList(filters, session)
    if not filters.useOnlyOwnerIds:
        catIds += getCatIdsFromSearchResults(filters, session)
    return catIds


def removeExpiredEntriesInCatCache(catDataDict: dict):
    keysToRemove = []
    catDataValue: CatData

    for catDataKey, catDataValue in catDataDict.items():
        if catDataValue.isCacheExpired():
            keysToRemove.append(catDataKey)
    for key in keysToRemove:
        del catDataDict[key]


def fillInCatBreedingInfo(catData: CatData, session):
    catIsTooOld = catData.getAge() >= AGE_WHEN_FEMALE_CANT_BREED_ANYMORE
    if catIsTooOld:
        catData.setCatCantBreed()
        return

    sleepForABit()
    offspringUrl = f'{CAT_OFFSPRING_URL}catid={catData.id}'
    response: str = None
    if USE_MOCK_DATA:
        response = mockOffspringPage
    else:
        print(f'Getting data from {offspringUrl}')

        def getOffspringResponse():
            response = session.get(offspringUrl, headers=REQUEST_HEADERS)
            response.raise_for_status()
            return response

        response = tryUntilSucceed(getOffspringResponse, functionName='getOffspringResponse',
                                   onErrorMessage=f'Trying to get offspring response again.')

    catData.fillInBreedingInfoWithHtml(response.text)


def fillInCat(catId: str, session):
    individualCatUrl = f'{INDIVIDUAL_CAT_PAGE_URL}catid={catId}'

    response: str = None
    if USE_MOCK_DATA:
        response = mockIndividualCatPage
    else:
        print(f'Getting data from {individualCatUrl}')
        response = session.get(
            individualCatUrl, headers=REQUEST_HEADERS)
        response.raise_for_status()

    catData = CatData()
    catData.initWithCatPageHtml(response.text)

    if catData.gender == Gender.FEMALE:
        fillInCatBreedingInfo(catData, session)

    # Confirm that the retrieved data matches the catId
    if catData.id != catId:
        raise ValueError(
            f"Retrieved cat's id doesn't match the catId we were fetching for. We were fetching id = {catId}, and we retrieved id = {catData.id}")
    return catData


def fillInCatDataDict(listOfCatIdsToFetch, catDataDict, session):
    if USE_MOCK_DATA:
        listOfCatIdsToFetch = ['2007722']
    for catId in listOfCatIdsToFetch:
        def fillInCatDictSpot():
            catData = fillInCat(catId, session)
            catDataDict[catData.id] = catData
            sleepForABit()

        tryUntilSucceed(fillInCatDictSpot, functionName='fillInCatDataDict',
                        onErrorMessage=f'Trying to fetch catId {catId} again.')


def getCatDataList(catIdsList: list[str], session, filters: MatchCatsFilters) -> list[CatData]:
    catDataDict = loadCatCache()
    if not filters.fromCacheOnly:
        removeExpiredEntriesInCatCache(catDataDict)

    if len(catIdsList) > 0:
        listOfCatIdsToFetch = []
        for catId in catIdsList:
            if catId not in catDataDict:
                listOfCatIdsToFetch.append(catId)

        fillInCatDataDict(listOfCatIdsToFetch, catDataDict, session=session)
        saveCatCache(catDataDict)

    for key in catDataDict:
        catDataDict[key].scoreCat(filters)

    def filterCatList(catData: CatData):
        if filters.useOnlyOwnerIds:
            catOwnerId = catData.owner.split('#')[-1].split(')')[0]
            if catOwnerId not in filters.additionalOwnerIds:
                return False

        # gender
        if catData.gender == Gender.FEMALE:
            if not catData.ableToGetPregnant and catData.getAge() > AGE_WHEN_CATS_START_BREEDING:
                return False
        if catData.gender == Gender.FEMALE_NEUTERED:
            if filters.gender != Gender.FEMALE_NEUTERED:
                return False
        if catData.gender == Gender.FEMALE_PREGNANT:
            if filters.gender != Gender.FEMALE_PREGNANT:
                return False
        if catData.gender == Gender.MALE_NEUTERED:
            if filters.gender != Gender.MALE_NEUTERED:
                return False
        if filters.gender != Gender.EITHER:
            if catData.gender != filters.gender:
                return False

        # age
        catAge = catData.getAge()
        if filters.maxAge and catAge > filters.maxAge:
            return False
        if filters.minAge and catAge < filters.minAge:
            print(
                f'rejecting cat with id {catData.id} because its age {catAge} is less than the minAge {filters.minAge}')
            return False

        # mood
        if filters.maxMoodDeviation and abs(float(catData.mood) - 50) > filters.maxMoodDeviation:
            return False

        # price
        exceedsSalePrice = (catData.salePrice > 0) and filters.maxSalePrice and (
            filters.maxSalePrice < catData.salePrice)
        exceedsStudFee = (catData.studFee > 0) and filters.maxStudFee and (
            filters.maxStudFee < catData.studFee)

        match filters.saleOrStud:
            case SaleOrStud.SALE:
                if exceedsSalePrice:
                    return False
            case SaleOrStud.STUD:
                if exceedsStudFee:
                    return False
            case SaleOrStud.SALE_OR_STUD:
                # Cat is only for sale
                if catData.salePrice <= 0:
                    if exceedsSalePrice:
                        return False
                # Cat is only for stud
                elif catData.studFee <= 0:
                    if exceedsStudFee:
                        return False
                # Cat is for sale and for stud
                elif exceedsSalePrice and exceedsStudFee:
                    return False
        return True

    # catDataList = list(catDataDict.values())
    catDataList = list(filter(filterCatList, list(catDataDict.values())))

    print(f'catDataList length = {len(catDataList)}')
    return catDataList


def fetchCats(filters: MatchCatsFilters):
    with requests.Session() as session:

        catIdsToFetch: list[str] = []
        if not filters.fromCacheOnly:
            if not USE_MOCK_DATA:
                login(session)
            catIdsToFetch = getCatIdsToFetch(filters, session)

        # print()
        # print(f'catIds length = {len(catIdsToFetch)}, and ids are as follows:')
        # for catId in catIdsToFetch:
        #     print(catId)

        # Get the HTML for each of the cat id's, parse it for cat info, and add it to the cat list
        return getCatDataList(catIdsToFetch, session=session, filters=filters)
