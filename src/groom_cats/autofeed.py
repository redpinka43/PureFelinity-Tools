
from bs4 import BeautifulSoup
import requests

from src.fetch_cats_payload_data import REQUEST_HEADERS
from src.groom_cats.grooming_constants import MINIMUM_MONEY_IN_ACCOUNT
from src.groom_cats.grooming_exceptions import NotEnoughMoneyException
from src.util import tryUntilSucceed

AMOUNT_OF_FOOD_TO_BUY = 500


buyFoodPayload = {
    'shoptype': 'food',
    'amount': AMOUNT_OF_FOOD_TO_BUY,
    'buyfood': 'Buy',
}

autofeedPayload = {
    'feedcats': 'Feed my cats'
}


def buyMoreFood(session):
    # Check if enough money
    try:
        def getFoodBuyPage():
            response = session.get('https://purefelinity.com/items/shop.php?shoptype=food',
                                   headers=REQUEST_HEADERS)
            response.raise_for_status()
            return response

        response = tryUntilSucceed(getFoodBuyPage, functionName='getFoodBuyPage',
                                   onErrorMessage=f'Trying to getFoodBuyPage.')
        text = BeautifulSoup(response.text, 'html.parser').text

        # If not enough money
        money = int(text.split('Money: $')[-1].split('\n')[0])
        print(f'money = {money}')
        if MINIMUM_MONEY_IN_ACCOUNT > money:
            raise NotEnoughMoneyException
        if money < AMOUNT_OF_FOOD_TO_BUY / 2:
            raise NotEnoughMoneyException
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # Buy food
    try:
        print('Buying more food...')
        response = session.post(
            'https://purefelinity.com/items/shop.php?shoptype=food', data=buyFoodPayload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    print(f'Successfully bought {AMOUNT_OF_FOOD_TO_BUY} units of food.')


def autofeed(session):
    try:
        # go to autofeeder page
        def getAutofeederPage():
            response = session.get('https://purefelinity.com/items/autofeeder.php',
                                   headers=REQUEST_HEADERS)
            response.raise_for_status()
            return response.text

        response = tryUntilSucceed(getAutofeederPage, functionName='getAutofeederPage',
                                   onErrorMessage=f'Trying to getAutofeederPage.')

        neededFood = int(response.split(
            'You need <b>')[-1].split('</b> units of basic food')[0])
        currentFood = int(response.split(
            'You have <b>')[-1].split('</b> units of basic food')[0])

        if neededFood == 0:
            print(f'Cats are fully fed.')
            return
        print('\nUsing autofeeder...')
        print(f'neededFood = {neededFood}')
        print(f'currentFood = {currentFood}')

        # if there isn't enough food, buy more
        while neededFood > currentFood:
            buyMoreFood(session)
            currentFood += AMOUNT_OF_FOOD_TO_BUY

    # if not enough money, skip this step and print that not enough money for food
    except NotEnoughMoneyException as fe:
        print(
            f'Not enough money to buy food while using autofeeder. Error: {fe}')
        return
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # feed the cats
    try:
        response = session.post(
            'https://purefelinity.com/items/autofeeder.php', data=autofeedPayload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    print('Autofeeder used successfully.')
