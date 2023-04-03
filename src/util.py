import logging
import time
import random

from bs4 import BeautifulSoup, ResultSet

DEFAULT_JSON_INDENT = 3

USE_MOCK_DATA = False

SLEEP_TIME_MIN = 0.2
SLEEP_TIME_MAX = 1
MAX_RETRY_TIMES = 100


def stringifyAttributes(obj):
    string = '{\n'
    attributes = vars(obj)
    for key, value in attributes.items():
        string += f'   {str(key)}: {str(value)}\n'
    string += '}'
    return string


def sleepForABit():
    if USE_MOCK_DATA:
        return
    sleepTime = random.uniform(SLEEP_TIME_MIN, SLEEP_TIME_MAX)
    time.sleep(sleepTime)


def tryUntilSucceed(function, functionName: str, onErrorMessage: str):
    succeeded = False
    retryCounter = 0
    while not succeeded:
        if retryCounter > MAX_RETRY_TIMES:
            print(f'Retried {functionName} too many times. Aborting.')
            return
        try:
            return function()
        except Exception as e:
            print(f'Exception caught in {functionName}(): {e}')
            logging.exception(e)
            print(onErrorMessage)
            retryCounter += 1


def getElementsByPartialText(soup: BeautifulSoup, tagType: str, text: str) -> list[ResultSet]:
    elements: list[ResultSet] = []
    for item in soup.find_all(tagType):
        if not text in item.text:
            continue
        elements.append(item)
    return elements


def getElementByPartialText(soup: BeautifulSoup, tagType: str, text: str) -> ResultSet:
    for item in soup.find_all(tagType):
        if not text in item.text:
            continue
        return item


def getElementTextByPartialText(soup: BeautifulSoup, tagType: str, text: str):
    for item in soup.find_all(tagType):
        if not text in item.text:
            continue
        return item.text.strip()


def goUpParentNTimes(element: ResultSet, times=1) -> ResultSet:
    newElement: ResultSet = element
    while (times > 0):
        if not newElement:
            raise ValueError('Expected newElement to have a value')
        newElement = newElement.parent
        times -= 1
    return newElement


def getKeyByValue(dict, val):
    for key, value in dict.items():
        if val == value:
            return key

    return "Key doesn't exist"


def getEndingS(number):
    return 's' if number != 1 else ''
