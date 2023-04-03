
import math
from bs4 import BeautifulSoup, ResultSet
import requests
from src.cat_search_result_data import CatSearchResultData
from src.fetch_cats_payload_data import REQUEST_HEADERS
from src.groom_cats.autofeed import NotEnoughMoneyException
from src.groom_cats.grooming_constants import MINIMUM_MONEY_IN_ACCOUNT
from src.groom_cats.grooming_exceptions import ErrorBuyingItem, NotEnoughGroomingItemsToBuy
from src.util import getElementByPartialText, getElementsByPartialText, getEndingS


CONDITION_WHEN_CAT_DOESNT_NEED_GROOMING = 95
ONE_BRUSHING_CONDITION_INCREASE = 5

itemNameToId = {
    'Double-Sided Brush': 20,
    'Grooming Glove': 25
}


def getGroomingItemsList(session):
    response = session.get(
        'https://purefelinity.com/items/index.php?type=grooming&status=all&submit=Submit', headers=REQUEST_HEADERS)
    response.raise_for_status()

    # Find all brush items
    soups = [BeautifulSoup(response.text, 'html.parser')]

    groomingItems: list[ResultSet] = []

    theresANextPage = 'Next' in soups[-1].text
    while theresANextPage:
        nextLink = getElementByPartialText(soup, "a", "Next").get('href')
        response = session.get(nextLink, headers=REQUEST_HEADERS)
        response.raise_for_status()

        soups.append(BeautifulSoup(response.text, 'html.parser'))
        theresANextPage = 'Next' in soups[-1].text

    for soup in soups:
        groomingItems = getElementsByPartialText(
            soup, 'b', 'Double-Sided Brush')
        groomingItems += getElementsByPartialText(soup, 'b', 'Grooming Glove')

        itemIds: list[str] = []
        item: ResultSet
        for item in groomingItems:
            useItemLink = item.parent.parent.findAll('form')[0].get('action')
            itemIds.append(useItemLink.split('?itemid=')[-1])
    return itemIds


class Item:
    def __init__(self, name, inStock, price):
        self.name = name
        self.inStock = inStock
        self.price = price


def getMoneyAvailable(session):
    response = session.get(
        'https://purefelinity.com/items/shop.php?shoptype=grooming', headers=REQUEST_HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return int(soup.text.split('Money: $')[-1].split('Home')[0].strip())


def buyItems(session, item: Item):
    # After buying each one, keep checking the shopping page if the item is still available, as well as your current money
    moneyAvailable = getMoneyAvailable(session)
    itemsBought = 0

    numItemsICanAfford = moneyAvailable // item.price
    numItemsICanBuy = numItemsICanAfford if item.inStock >= numItemsICanAfford else item.inStock

    while numItemsICanBuy > 0:
        try:
            response = session.post(
                f'https://purefelinity.com/items/buy.php', data={
                    'itemid': itemNameToId[item.name],
                    'buyshop': 'Buy'
                })
            response.raise_for_status()

            # Check that the item was bought succesfully
            purchaseSuccessful = 'You bought the ' in response.text

            if not purchaseSuccessful:
                raise ErrorBuyingItem

            numItemsICanBuy -= 1
            itemsBought += 1
            moneyAvailable = getMoneyAvailable(session)

        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    return itemsBought


def buyMoreGroomingItems(session):
    # Go to https://purefelinity.com/items/shop.php?shoptype=grooming and see if
    # Double-Sided Brush or Grooming Glove are there
    items = {}

    response = session.get(
        'https://purefelinity.com/items/shop.php?shoptype=grooming', headers=REQUEST_HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    def getItem(itemName):
        queriedEl = getElementByPartialText(soup, "b", itemName)
        if queriedEl is None:
            return Item(itemName, 0, 0)
        itemGroup = queriedEl.parent
        numOfItem = int(itemGroup.text.split('In stock:')
                        [-1].split('Number of uses:')[0])
        price = int(itemGroup.text.split(
            'Price: $')[-1].split('In stock:')[0])
        return Item(itemName, numOfItem, price)

    items['doubleSidedBrush'] = getItem("Double-Sided Brush")
    items['groomingGlove'] = getItem("Grooming Glove")

    if items['groomingGlove'].inStock == 0 and items['groomingGlove'].inStock == 0:
        raise NotEnoughGroomingItemsToBuy

    moneyAvailable = getMoneyAvailable(session)

    if MINIMUM_MONEY_IN_ACCOUNT > moneyAvailable:
        raise NotEnoughMoneyException
    if items['doubleSidedBrush'].price > moneyAvailable and items['groomingGlove'].price > moneyAvailable:
        raise NotEnoughMoneyException

    # If you can afford grooming gloves, buy them
    itemsBought = 0
    try:
        itemsBought += buyItems(session, items['groomingGlove'])
        itemsBought += buyItems(session, items['doubleSidedBrush'])
    except ErrorBuyingItem as _be:
        print('Error buying item. Not sure what happened.')


def getBrushPayload(catId, numTimesToGroom):
    return {
        'type': 'grooming',
        'status': 'all',
        'catid': catId,
        'use2': 'groom cat',
        'amount': numTimesToGroom
    }


def brushCats(session, cats: list[CatSearchResultData]):
    print(f'\nBrushing cats...')
    catIndex = 0
    numTimesGroomed = 0
    numCatsGroomed = 0
    itemsUsedUp = 0

    def printFinalStatsMsg():
        print(
            f'Finished brushing cats, groomed {numCatsGroomed} cat{getEndingS(numCatsGroomed)} and used up {itemsUsedUp} item{getEndingS(itemsUsedUp)}.')

    # Fetch the list of item id's.
    groomingItemsList = getGroomingItemsList(session)

    def goToNextCat(cat: CatSearchResultData):
        nonlocal catIndex
        nonlocal numCatsGroomed
        nonlocal numTimesGroomed

        if numTimesGroomed > 0:
            print(
                f'Brushed {cat.name} {numTimesGroomed} time{getEndingS(numTimesGroomed)}.')
            numCatsGroomed += 1
        numTimesGroomed = 0
        catIndex += 1

    # Iterate through the cat list, grooming each cat as you go
    while catIndex < len(cats):
        cat = cats[catIndex]
        if numTimesGroomed >= 5:
            goToNextCat(cat)
            continue
        if cat.condition > CONDITION_WHEN_CAT_DOESNT_NEED_GROOMING:
            goToNextCat(cat)
            continue

        # How many times should we groom the cat?
        # 95 - 87 = 8 -> 2 times
        numTimesToGroom = math.ceil((CONDITION_WHEN_CAT_DOESNT_NEED_GROOMING -
                                    cat.condition) / ONE_BRUSHING_CONDITION_INCREASE)

        # Check if we need to buy more grooming items
        if len(groomingItemsList) == 0:
            try:
                buyMoreGroomingItems(session)
                groomingItemsList = getGroomingItemsList(session)
            except NotEnoughGroomingItemsToBuy as _ge:
                print(
                    f'\nNot enough grooming items to buy in the shop. Continuing without finishing grooming.')
                printFinalStatsMsg()
                return
            except NotEnoughMoneyException as _fe:
                print(
                    f'\nNot enough money to buy grooming items. Continuing without finishing grooming.')
                printFinalStatsMsg()
                return
            # continue?

        # Groom the kitty
        try:
            response = session.post(
                f'https://purefelinity.com/items/item_action.php?itemid={groomingItemsList[0]}', data=getBrushPayload(cat.id, numTimesToGroom))
            response.raise_for_status()

            catWalkedAway = "thinks it's time for a nap" in response.text
            if catWalkedAway:
                goToNextCat(cat)
                continue

            # Get # of successful groomings from response
            numSuccessfulGroomings = response.text.count('better condition')
            numUnsuccessfulGroomings = response.text.count(
                'You notice no changes about your cat. Oh well, maybe next time.')

            print(
                f'Number of successful groomings: {numSuccessfulGroomings}, number of unsuccessful groomings: {numUnsuccessfulGroomings}')

            numTimesGroomed += numSuccessfulGroomings + numUnsuccessfulGroomings
            cat.condition += ONE_BRUSHING_CONDITION_INCREASE * numSuccessfulGroomings

            itemIsExpired = response.text.count(
                'In other words, there are no uses left for this item.') > 0
            if itemIsExpired:
                groomingItemsList.pop(0)
                itemsUsedUp += 1

        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    printFinalStatsMsg()
    print('All cats have been groomed for today :)')
