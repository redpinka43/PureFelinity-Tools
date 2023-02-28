from src.fetch_cats import REQUEST_HEADERS
from src.fetch_cats_payload_data import *
from src.match_cats_filters import MatchCatsFilters
from src.mock_data import *
from src.cat_search_result_data import *
from bs4 import BeautifulSoup, ResultSet

from src.util import USE_MOCK_DATA, sleepForABit, tryUntilSucceed


RESULTS_PER_PAGE = 20


def getSimplifiedGender(gender: Gender) -> str:
    if gender is Gender.EITHER:
        return Gender.EITHER
    if gender is Gender.FEMALE or gender is Gender.FEMALE_NEUTERED or gender is Gender.FEMALE_PREGNANT:
        return Gender.FEMALE
    return Gender.MALE


def getSearchPageRequestUrl(filters: MatchCatsFilters, page=0):
    # later we could perhaps use the 'search by trait' feature
    url = CAT_SEARCH_REQUEST_URL

    if 0 < page:
        url += f'start={page * RESULTS_PER_PAGE}&'

    url += 'breed=any'

    simplifiedGender = getSimplifiedGender(filters.gender)
    url += f'&gender={simplifiedGender.value}'

    if filters.maxAge:
        url += f'&maxage={filters.maxAge}'

    url += f'&sale_or_stud={filters.saleOrStud.value}'
    url += '&breeder=&catsearch=Search'
    return url


def getNumberOfSearchResultPages(searchPageHtml) -> int:
    soup = BeautifulSoup(searchPageHtml, 'html.parser')
    pagesDivList = soup.find_all("div", {"class": "art-pager"})

    if len(pagesDivList) == 0:
        return 1

    if len(pagesDivList) > 1:
        raise ValueError(
            f"pagesDiv's length was expected to be 0 or 1, received {len(pagesDivList)} instead")
    pagesDiv = pagesDivList[0]
    links = pagesDiv.find_all('a')

    # Find last page number
    lastPageNumber = None
    for i in reversed(range(1, len(links))):
        if links[i].get_text() == 'Next':
            lastPageNumber = links[i - 1].get_text()
            break

    if not lastPageNumber:
        return 1
    return int(lastPageNumber)


def getCatIdsFromPage(searchResultsPage, filters: MatchCatsFilters) -> list[str]:
    # Get list of cat rows
    soup = BeautifulSoup(searchResultsPage, 'html.parser')

    # Get all elements with the following:
    catRows: ResultSet = []
    catRows += soup.find_all('tr', {"bgcolor": "#E8E0D2"})
    catRows += soup.find_all('tr', {"bgcolor": "#F1EADE"})

    catSearchResultDatas = convertHtmlRowsToCatSearchResultDatas(catRows)

    # If CatSearchResultData.matchesFilter(filter), add the cat's id to the list
    catIds = []
    data: CatSearchResultData
    for data in catSearchResultDatas:
        if data.matchesFilter(filters):
            catIds.append(data.id)
    return catIds


def getCatIdsFromSearchResults(filters: MatchCatsFilters, session) -> list[str]:
    firstSearchRequestUrl = getSearchPageRequestUrl(filters)
    searchResultPages = []
    if USE_MOCK_DATA:
        print('Using mock data.')
        searchResultPages.append(mockSearchResultPages0.text)
        searchResultPages.append(mockSearchResultPages0.text)
    else:
        print('Fetching real data.')
        print(f'url = {firstSearchRequestUrl}')

        def getFirstSearchRequestUrl():
            response = session.get(firstSearchRequestUrl,
                                   headers=REQUEST_HEADERS)
            response.raise_for_status()
            return response

        response = tryUntilSucceed(getFirstSearchRequestUrl, functionName='getFirstSearchRequestUrl',
                                   onErrorMessage=f'Trying to get first search request url again.')
        searchResultPages.append(response.text)

    numberOfSearchResultPages = getNumberOfSearchResultPages(
        searchResultPages[0])

    if not USE_MOCK_DATA:
        for i in range(1, numberOfSearchResultPages):
            pageRequestUrl = getSearchPageRequestUrl(filters, page=i)
            print(f'pageRequestUrl = {pageRequestUrl}')

            def getSearchResultPage():
                response = session.get(pageRequestUrl, headers=REQUEST_HEADERS)
                response.raise_for_status()
                return response

            response = tryUntilSucceed(getSearchResultPage, functionName='getSearchResultPage',
                                       onErrorMessage=f'Trying to get search result page again.')
            searchResultPages.append(response.text)
            sleepForABit()

    print(f'searchResultPages.length = {len(searchResultPages)}')

    # Create a list of cat id's, fetched from the searchResultPages list
    catIds = []
    for page in searchResultPages:
        catIds += getCatIdsFromPage(page, filters)

    return catIds
