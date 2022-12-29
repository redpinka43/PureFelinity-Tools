from src.util import stringifyAttributes


class CatCoatData:
    def __init__(self):
        self.length = None
        self.texture = ''
        self.baseColor = None
        self.bicolor = None
        self.tabbyPattern = None
        self.albino = None
        self.ghostmarking = False
        self.rufused = False
        self.golden = None
        self.silver = None
        self.smoke = None

    def __str__(self):
        return stringifyAttributes(self)


def areAttributesEqual(first, second):
    if first and second and first != second:
        return False
    return True


def catCoatDatasMatchTextureAndLength(first: CatCoatData, second: CatCoatData):
    if not (first.length == 'any' or second.length == 'any'):
        if not areAttributesEqual(first.length, second.length):
            return False
    if not (first.texture == 'any' or second.texture == 'any'):
        if not areAttributesEqual(first.texture, second.texture):
            return False
    return True


def catCoatDatasMatchColor(first: CatCoatData, second: CatCoatData):
    if not areAttributesEqual(first.baseColor, second.baseColor):
        return False
    if not areAttributesEqual(first.bicolor, second.bicolor):
        return False

    # Tabby
    if first.tabbyPattern == 'any':
        if not second.tabbyPattern:
            return False
    elif second.tabbyPattern == 'any':
        if not first.tabbyPattern:
            return False
    if not areAttributesEqual(first.tabbyPattern, second.tabbyPattern):
        return False

    # Albino
    if first.albino == 'any':
        if not second.albino:
            return False
    elif second.albino == 'any':
        if not first.albino:
            return False
    else:
        if not areAttributesEqual(first.albino, second.albino):
            return False

    if not areAttributesEqual(first.ghostmarking, second.ghostmarking):
        return False
    if not areAttributesEqual(first.rufused, second.rufused):
        return False
    if not areAttributesEqual(first.golden, second.golden):
        return False
    if not areAttributesEqual(first.silver, second.silver):
        return False
    if not areAttributesEqual(first.smoke, second.smoke):
        return False
    return True
