import requests
from src.groom_cats.autofeed import autofeed
from src.groom_cats.brush_cats import brushCats
from src.groom_cats.get_cats_to_groom import fillInCatGroomStats, getCatsToGroom
from src.groom_cats.users_info import *
from src.groom_cats.vet_cats import vetCats
from src.groom_cats.website_data import *
from src.util import getKeyByValue


USER_ID = LocationsClass.a2_Kittystix2()


def getUsername() -> str:
    return getKeyByValue(USERS, USER_ID)


def login(session):
    try:
        myLoginPayload = {**loginPayload, 'username': getUsername()}
        response = session.post(LOGIN_URL, data=myLoginPayload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    print(f'Successfully logged in as {getUsername()}.\n')


def goToBank(session):
    try:
        response = session.get(
            'https://purefelinity.com/bank.php', headers=REQUEST_HEADERS)
        response.raise_for_status()

        canGoToBank = 'You have already been to the bank this week' in response.text
        if not canGoToBank:
            newMoney = int(response.text.split(
                'You are allowed to withdraw $')[-1].split('per week')[0])
            response = session.post(
                f'https://purefelinity.com/bank.php', data={'getmoney': 'Get Money'})
            response.raise_for_status()

            print(f'Went to bank, got ${newMoney}.')
        else:
            print("Already went to the bank this week.")

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def groomCats():
    with requests.Session() as session:
        cats: list[str] = []

        login(session)
        goToBank(session)
        autofeed(session)
        cats = getCatsToGroom(USER_ID, session)
        fillInCatGroomStats(session, cats)

        vetCats(session, cats)
        brushCats(session, cats)


success = groomCats()
if success:
    print(f'\nFinished successfully.')
