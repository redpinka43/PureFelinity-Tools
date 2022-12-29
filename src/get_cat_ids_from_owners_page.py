from bs4 import element, BeautifulSoup, ResultSet
from src.cat_search_result_data import *
from src.fetch_cats_payload_data import REQUEST_HEADERS, USER_CATS_PAGE_URL
from src.match_cats_filters import MatchCatsFilters
from src.util import getElementByPartialText, getElementTextByPartialText, goUpParentNTimes, sleepForABit, tryUntilSucceed

RESULTS_PER_PAGE = 15


def getOwnersCatsUrl(ownerId, page=0):
    url = USER_CATS_PAGE_URL
    if 0 < page:
        url += f'start={page * RESULTS_PER_PAGE}&'
    url = f'{url}user={ownerId}'

    return url


def getNumberOfPages(searchPageHtml) -> int:
    soup = BeautifulSoup(searchPageHtml, 'html.parser')

    text = getElementTextByPartialText(soup, "p", "Cats:")
    if 'Next' in text:
        finalPageNumber = int(text.strip('Next').split()[-1])
        return finalPageNumber
    else:
        return 1


def convertRowToCatSearchResultData(row: ResultSet):
    data = CatSearchResultData()

    cells = row.findChildren(recursive=False)

    # id
    catHref = cells[0].find_all('a', href=True)[0].get("href")
    data.id = catHref.split('=')[-1]

    # gender
    data.gender = getGenderFromString(cells[2].text.strip())

    # age
    data.age = int(cells[4].text.strip('m) ').split('(')[-1])

    return data


def convertRowsToCatSearchResultDatas(htmlRows: list[ResultSet]) -> list[CatSearchResultData]:
    datas = []

    row: ResultSet
    for row in htmlRows:
        datas.append(convertRowToCatSearchResultData(row))
    return datas


def getCatIdsFromPage(searchResultsPage, filters: MatchCatsFilters) -> list[str]:
    soup = BeautifulSoup(searchResultsPage, 'html.parser')
    catIds = []

    # If no cats, return nothing
    noCatsText = getElementTextByPartialText(
        soup, "p", "This user doesn't have any cats")
    if noCatsText:
        return catIds

    # Get list of cat rows
    fullnessHeader = getElementByPartialText(soup, "b", "Fullness")
    if not fullnessHeader:
        raise ValueError('Expected fullnessHeader to exist')

    catRowsTableChildren = goUpParentNTimes(
        fullnessHeader, 7).findChildren(recursive=False)

    catRows: list[ResultSet] = []
    for i in range(2, len(catRowsTableChildren), 2):
        catRows.append(catRowsTableChildren[i])

    catSearchResultDatas = convertRowsToCatSearchResultDatas(catRows)

    # If CatSearchResultData.matchesFilter(filter), add the cat's id to the list
    data: CatSearchResultData
    for data in catSearchResultDatas:
        if data.matchesFilter(filters, ignorePrice=True):
            catIds.append(data.id)
    return catIds


def getCatIdsFromOwnersList(filters: MatchCatsFilters, session) -> list[str]:
    catIds = []

    for ownerId in filters.additionalOwnerIds:
        firstOwnerPageUrl = getOwnersCatsUrl(ownerId)
        ownersCatsPages = []

        def getFirstPage():
            response = session.get(firstOwnerPageUrl,
                                   headers=REQUEST_HEADERS)
            response.raise_for_status()
            return response

        response = tryUntilSucceed(getFirstPage, functionName='getFirstPage',
                                   onErrorMessage=f'Trying to get first page of owner with id = {ownerId} again.')
        ownersCatsPages.append(response.text)

        numberOfPages = getNumberOfPages(
            ownersCatsPages[0])

        for i in range(1, numberOfPages):
            pageRequestUrl = getOwnersCatsUrl(ownerId, page=i)
            print(f'pageRequestUrl = {pageRequestUrl}')

            def getOwnersCatsPage():
                response = session.get(pageRequestUrl, headers=REQUEST_HEADERS)
                response.raise_for_status()
                return response

            response = tryUntilSucceed(getOwnersCatsPage, functionName='getOwnersCatsPage',
                                       onErrorMessage=f'Trying to get search result page again.')
            ownersCatsPages.append(response.text)
            sleepForABit()

        # Create a list of cat id's, fetched from the searchResultPages list
        for page in ownersCatsPages:
            catIds += getCatIdsFromPage(page, filters)

    return catIds
