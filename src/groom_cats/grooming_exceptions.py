
class NotEnoughMoneyException(Exception):
    "Raised when there isn't enough money to buy something."
    pass


class ErrorBuyingItem(Exception):
    "Raised when attempting to buy an item fails."
    pass


class NotEnoughGroomingItemsToBuy(Exception):
    "Raised when there aren't enough groomings items in the shop to buy."
    pass
