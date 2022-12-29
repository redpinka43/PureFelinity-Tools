from enum import Enum


class Gender(Enum):
    EITHER = 'either'
    FEMALE = 'female'
    FEMALE_NEUTERED = 'female (neutered)'
    FEMALE_PREGNANT = 'female (pregnant)'
    MALE = 'male'
    MALE_NEUTERED = 'male (neutered)'


class SaleOrStud(Enum):
    SALE_OR_STUD = 'both'
    SALE = 'sale'
    STUD = 'stud'
