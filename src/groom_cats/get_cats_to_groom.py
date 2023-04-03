
from bs4 import BeautifulSoup, ResultSet
import requests
from src.cat_search_result_data import CatSearchResultData
from src.get_cat_ids_from_owners_page import convertRowsToCatSearchResultDatas
from src.groom_cats.website_data import *
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


def getCatDatasFromPage(searchResultsPage) -> list[CatSearchResultData]:
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

    data: CatSearchResultData
    for i, data in enumerate(catSearchResultDatas):
        print(f'\t{data.name}')
    return catSearchResultDatas


def getCatsToGroom(ownerId, session) -> list[CatSearchResultData]:
    print('\nGetting cats to groom...')
    catDatas = []

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
        # print(f'pageRequestUrl = {pageRequestUrl}')

        def getOwnersCatsPage():
            response = session.get(pageRequestUrl, headers=REQUEST_HEADERS)
            response.raise_for_status()
            return response

        response = tryUntilSucceed(getOwnersCatsPage, functionName='getOwnersCatsPage',
                                   onErrorMessage=f'Trying to get search result page again.')
        ownersCatsPages.append(response.text)
        sleepForABit()

    # Create a list of cat id's, fetched from the searchResultPages list
    print(f'Cats found:')
    for page in ownersCatsPages:
        catDatas += getCatDatasFromPage(page)
    return catDatas


def fillInCatGroomStats(session, cats):
    print("\nFilling in cat's stats...")
    cat: CatSearchResultData
    for cat in cats:
        try:
            def getCatPage():
                response = session.get(f'https://purefelinity.com/viewcat.php?catid={cat.id}',
                                       headers=REQUEST_HEADERS)
                response.raise_for_status()
                return response.text

            html = tryUntilSucceed(getCatPage, functionName='getCatPage',
                                   onErrorMessage=f'Trying to getCatPage.')

            soup = BeautifulSoup(html, 'html.parser')

            # health
            cat.health = float(getElementByPartialText(
                soup, 'b', 'Health:').parent.parent.findChildren(recursive=False)[2].text)

            # coat condition
            cat.condition = float(getElementByPartialText(
                soup, 'b', 'Coat Condition:').parent.parent.findChildren(recursive=False)[2].text)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
