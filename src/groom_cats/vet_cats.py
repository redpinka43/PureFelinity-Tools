from src.cat_search_result_data import CatSearchResultData
from src.fetch_cats_payload_data import REQUEST_HEADERS

MAX_HEALTH_TO_VET = 92


def vetCats(session, cats):
    print(f'Vetting cats...')
    cat: CatSearchResultData
    for cat in cats:
        if cat.health < MAX_HEALTH_TO_VET:
            print(f'Vetting {cat.name}')
            response = session.get(
                f'https://purefelinity.com/vet.php?catvet={cat.id}&n=y', headers=REQUEST_HEADERS)
            response.raise_for_status()
