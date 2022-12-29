import os
import jsonpickle
from src.cat_data import CatData
from src.file_utils import createDirectory
from src.util import DEFAULT_JSON_INDENT


CAT_CACHE_DIRECTORY = "cache"
CAT_CACHE_FILE_NAME = f"{CAT_CACHE_DIRECTORY}/cat_data_cache.txt"


def loadCatCache() -> dict:
    cacheExists = os.path.exists(CAT_CACHE_FILE_NAME)
    if not cacheExists:
        return {}
    with open(CAT_CACHE_FILE_NAME, 'r') as f:
        decoded = jsonpickle.decode(f.read())
        return decoded


def saveCatCache(catDataList: dict):
    createDirectory(CAT_CACHE_DIRECTORY)
    with open(CAT_CACHE_FILE_NAME, 'w') as f:
        json_object = jsonpickle.encode(
            catDataList, indent=DEFAULT_JSON_INDENT)
        f.write(json_object)
