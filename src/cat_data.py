import datetime
import re
import sys
from bs4 import BeautifulSoup
from define_filters import NUMBER_OF_DAYS_IN_WHICH_WE_WILL_BE_BREEDING
from src.cat_coat_data import CatCoatData, catCoatDatasMatchColor, catCoatDatasMatchTextureAndLength
from src.match_cats_filters import MatchCatsFilters
from src.util import getElementTextByPartialText, stringifyAttributes
from src.enums import *


CACHE_EXPIRES_WHEN_THIS_OLD_IN_DAYS = 2
NUMBER_OF_DAYS_FEMALE_CAN_BREED_AFTER = 13 - \
    NUMBER_OF_DAYS_IN_WHICH_WE_WILL_BE_BREEDING

AGE_WHEN_CATS_START_BREEDING = 10
AGE_WHEN_FEMALE_CANT_BREED_ANYMORE = 80
RESCUE_SHELTER_ADOPTION_PRICE = 200


class CatScore:
    def __init__(self):
        self.bodyType = 0
        self.bodySize = 0
        self.headShape = 0
        self.ears = 0
        self.noseLength = 0
        self.eyeShape = 0
        self.eyeColor = 0
        self.coat = 0
        self.tail = 0
        self.legs = 0
        self.color = 0

    def __str__(self):
        return stringifyAttributes(self)

    def getTraitsArray(self):
        attributes = vars(self)
        traitsArray = []
        for _key, value in attributes.items():
            traitsArray.append(value)
        return traitsArray

    def getImperfectTraitsScore(self):
        total = 0
        for traitScore in self.getTraitsArray():
            if traitScore != 0:
                total += 1
        return total

    def getTotalTraitDeviancy(self):
        total = 0
        for traitScore in self.getTraitsArray():
            total += abs(traitScore)
        return total


class CatData:
    def __init__(self, cacheDate: datetime.date = None):
        self.id = 0

        self.score = CatScore()

        self.cacheDate = cacheDate or datetime.date.today()
        self.name = 0
        self.owner = 0
        self.salePrice = 0
        self.studFee = 0
        self.birthDate = 0
        self.gender = None
        self.breed = 0

        # Body
        self.bodyType = 0
        self.bodySize = 0
        self.headShape = 0
        self.earSize = 0
        self.earCurl = 0
        self.noseLength = 0
        self.eyeShape = 0
        self.eyeColor = 0
        self.eyeDepth = 0
        self.tail = 0
        self.legs = 0

        # Coat
        self.coat = CatCoatData()

        # Family
        self.showPoints = 0
        self.ageOfMostRecentOffspring = 0
        self.ableToGetPregnant = None

        # Care status
        self.fullness = 0
        self.health = 0
        self.coatCondition = 0
        self.activeness = 0
        self.attitude = 0
        self.mood = 0

    def __str__(self):
        return stringifyAttributes(self)

    def getAge(self):
        return (datetime.date.today() - self.birthDate).days

    csvHeader = 'id imperfectTraitsScore totalTraitDeviancy cacheDate name owner salePrice studFee age gender breed scoreBodyType scoreBodySize scoreHeadShape scoreEars scoreNoseLength scoreEyeShape scoreEyeColor scoreCoat scoreColor scoreTail scoreLegs bodyType bodySize headShape earSize earCurl noseLength eyeShape eyeColor eyeDepth tail legs coatLength coatTexture coatBaseColor coatBicolor coatTabbyPattern coatAlbino coatGhostMarking coatRufused coatGolden coatSilver coatSmoke showPoints ageOfMostRecentOffspring ableToGetPregnant fullness health coatCondition activeness attitude mood'

    def getCsvHeader():
        return CatData.csvHeader.split(' ')

    def convertToCsvRow(self):
        cells = []
        cells.append(self.id)
        cells.append(self.score.getImperfectTraitsScore())
        cells.append(self.score.getTotalTraitDeviancy())
        cells.append(self.cacheDate)
        cells.append(self.name)
        cells.append(self.owner)
        cells.append(self.salePrice)
        cells.append(self.studFee)
        cells.append(self.getAge())
        cells.append(self.gender.value)
        cells.append(self.breed)
        cells.append(self.score.bodyType)
        cells.append(self.score.bodySize)
        cells.append(self.score.headShape)
        cells.append(self.score.ears)
        cells.append(self.score.noseLength)
        cells.append(self.score.eyeShape)
        cells.append(self.score.eyeColor)
        cells.append(self.score.coat)
        cells.append(self.score.color)
        cells.append(self.score.tail)
        cells.append(self.score.legs)
        cells.append(self.bodyType)
        cells.append(self.bodySize)
        cells.append(self.headShape)
        cells.append(self.earSize)
        cells.append(self.earCurl)
        cells.append(self.noseLength)
        cells.append(self.eyeShape)
        cells.append(self.eyeColor)
        cells.append(self.eyeDepth)
        cells.append(self.tail)
        cells.append(self.legs)
        cells.append(self.coat.length)
        cells.append(self.coat.texture)
        cells.append(self.coat.baseColor)
        cells.append(self.coat.bicolor)
        cells.append(self.coat.tabbyPattern)
        cells.append(self.coat.albino)
        cells.append(self.coat.ghostmarking)
        cells.append(self.coat.rufused)
        cells.append(self.coat.golden)
        cells.append(self.coat.silver)
        cells.append(self.coat.smoke)
        cells.append(self.showPoints)
        cells.append(self.ageOfMostRecentOffspring)
        cells.append(self.ableToGetPregnant)
        cells.append(self.fullness)
        cells.append(self.health)
        cells.append(self.coatCondition)
        cells.append(self.activeness)
        cells.append(self.attitude)
        cells.append(self.mood)
        return cells

    def isCacheExpired(self):
        daysSinceCaching = (datetime.date.today() - self.cacheDate).days
        cacheIsExpired = CACHE_EXPIRES_WHEN_THIS_OLD_IN_DAYS <= daysSinceCaching
        return cacheIsExpired

    def initWithCatPageHtml(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        # id
        text = getElementTextByPartialText(soup, "p", "ID#:")
        text = text.removeprefix("ID#:").strip()
        self.id = text.split()[0]

        # name
        el = soup.find_all("div", {"class": "interiorMargin"})[0]
        if len(el.find_all("big")) > 0:
            # If you don't own the cat, the name will be in a "big" tag
            self.name = el.find_all("big")[0].text
        else:
            def getNameField():
                inputs = el.find_all("input")
                for input in inputs:
                    if input.get("name") == "name_new":
                        return input
            # If you own the cat, the name will be in a text box
            self.name = getNameField().get("value")

        # owner
        text = getElementTextByPartialText(soup, "p", "Owner:")
        text = text.removeprefix("Owner:").strip()
        self.owner = text.split('Breeder:')[0].strip()

        # salePrice
        text = getElementTextByPartialText(soup, "p", "Sale Price:")
        if text:
            self.salePrice = int(text.split("Sale Price:")[
                1].split("Buy")[0].strip('$ '))
        if 'Rescue Shelter' in self.owner:
            self.salePrice = RESCUE_SHELTER_ADOPTION_PRICE

        # studFee
        text = getElementTextByPartialText(soup, "p", "Stud fee:")
        if text:
            studFeeText = text.split("Stud fee:")[1].strip('$ ')
            if '(private)' in studFeeText:
                self.studFee = 0
            else:
                self.studFee = int(studFeeText)

        # birthDate
        text = getElementTextByPartialText(soup, "p", "Age:")
        ageInDays = text.split('month')[0].split()[-1].strip('(')
        self.birthDate = datetime.date.today() - datetime.timedelta(int(ageInDays))

        # gender
        text = getElementTextByPartialText(soup, 'p', 'Gender:').split('Gender:')[
            1].split('Age')[0].strip()
        text = text.split('Bred to:')[0]
        self.gender = Gender(text)

        # breed
        def getBreed():
            for a in soup.find_all('a', href=True):
                if 'standards.php?breed=' in a['href']:
                    return a.text
            return 'mixed breed'
        self.breed = getBreed()

        # Number attributes
        text = getElementTextByPartialText(
            soup, 'p', 'Body type:')
        self.bodyType = int(text.split('Body type:')[
                            1].split('(')[1].split(')')[0])
        self.bodySize = int(text.split('Body size:')[
                            1].split('(')[1].split(')')[0])
        self.headShape = int(text.split('Head shape:')[
            1].split('(')[1].split(')')[0])
        self.earSize = int(text.split('Ears:')[1].split('(')[1].split(')')[0])
        self.earCurl = text.split('Ears:')[1].split(
            '(')[0].strip().split(' ')[-1]
        self.noseLength = int(text.split(
            'Nose:')[1].split('(')[1].split(')')[0])
        self.eyeShape = int(text.split('Eyes:')[1].split('(')[1].split(')')[0])

        # Other attributes
        eyeText = text.split('Eye color:')[1].split('Coat:')[0].strip()
        self.eyeColor = ' '.join(eyeText.split()[1:])
        self.eyeDepth = text.split('Eye color:')[1].split('Coat:')[
            0].strip().split()[0].strip()
        self.tail = text.split('Tail:')[1].split('Legs:')[0].strip()
        self.legs = text.split('Legs:')[1].strip()

        # Coat
        self.coat.length = text.split('Coat:')[1].split('Tail:')[
            0].split()[0].strip()
        textureText = text.split('Coat:')[1].split('Tail:')[
            0].split()[1:]
        self.coat.texture = ' '.join(textureText)

        def getCoatColorText():
            # Find breed text
            for a in soup.find_all('a', href=True):
                if 'standards.php?breed=' in a['href']:
                    return a.parent.parent.text.split(',')[1].strip()
            return getElementTextByPartialText(soup, 'p', 'mixed breed').split(',')[1].strip()
        coatColorText = getCoatColorText()
        self.coat.baseColor = coatColorText.split()[0]

        def getCoatBicolorText():
            if ' bicolor' in coatColorText:
                return 'bicolor'
            if ' mitted' in coatColorText:
                return 'mitted'
            if ' van' in coatColorText:
                return 'van'
            if ' harlequin' in coatColorText:
                return 'harlequin'
            return None
        self.coat.bicolor = getCoatBicolorText()

        def getTabbyPatternText():
            if ' classic tabby' in coatColorText:
                return 'classic tabby'
            if ' mackerel tabby' in coatColorText:
                return 'mackerel tabby'
            if ' ticked tabby' in coatColorText:
                return 'ticked tabby'
            if ' spotted tabby' in coatColorText:
                return 'spotted tabby'
            return None

        self.coat.tabbyPattern = getTabbyPatternText()

        def getAlbinoText():
            if ' point' in coatColorText:
                return 'point'
            if ' mink' in coatColorText:
                return 'mink'
            if ' burmese' in coatColorText:
                return 'burmese'
            return None

        self.coat.albino = getAlbinoText()

        self.coat.ghostmarking = 'ghostmarking' in coatColorText
        self.coat.rufused = 'rufus' in coatColorText
        self.coat.golden = 'golden' in coatColorText
        self.coat.silver = 'silver' in coatColorText
        self.coat.smoke = 'smoke' in coatColorText

        text = getElementTextByPartialText(soup, 'p', 'Show wins (sp:')
        if text:
            self.showPoints = text.split('sp:')[1].split(')')[0].strip()
        else:
            self.showPoints = 0

        text = getElementTextByPartialText(soup, 'tr', 'Fullness:')
        self.fullness = text.split('Fullness:')[1].split('hungry')[0].strip()
        self.health = text.split('Health:')[1].split('sick')[0].strip()
        self.coatCondition = text.split('Coat Condition:')[
            1].split('bad')[0].strip()
        self.activeness = text.split('Activeness:')[1].split('lazy')[0].strip()
        self.attitude = text.split('Attitude:')[1].split('reserved')[0].strip()
        self.mood = text.split('Mood:')[1].split('shy')[0].strip()

    def setCatCantBreed(self):
        self.ageOfMostRecentOffspring = None
        self.ableToGetPregnant = False

    def fillInBreedingInfoWithHtml(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        self.ableToGetPregnant = self.getAge() >= AGE_WHEN_CATS_START_BREEDING

        noOffspringText = getElementTextByPartialText(
            soup, 'i', 'has no offspring.')
        if noOffspringText:
            return

        offspringRows = soup.find_all('tr', {'bgcolor': '#F1EADE'})
        offspringRows += soup.find_all('tr', {'bgcolor': '#fbf6ec'})
        # Keep only every other row, starting with 1
        offspringRows = offspringRows[0::2]

        youngestOffspringAge = sys.maxsize
        for row in offspringRows:
            lastWordInRow = row.text.split()[-1]
            age = int(re.findall('\d+', lastWordInRow)[0])
            if youngestOffspringAge > age:
                youngestOffspringAge = age

        self.ageOfMostRecentOffspring = youngestOffspringAge
        self.ableToGetPregnant = youngestOffspringAge >= NUMBER_OF_DAYS_FEMALE_CAN_BREED_AFTER

    def scoreCat(self, filters: MatchCatsFilters):
        self.score.bodyType = self.bodyType - filters.bodyType if filters.bodyType else 0
        self.score.bodySize = self.bodySize - filters.bodySize if filters.bodySize else 0
        self.score.headShape = self.headShape - \
            filters.headShape if filters.headShape else 0

        # ears
        self.score.ears = self.earSize - filters.earSize if filters.earSize else 0
        if filters.earCurl and filters.earCurl != self.earCurl:
            parity = 1 if self.score.ears >= 0 else -1
            self.score.ears += parity

        self.score.noseLength = self.noseLength - \
            filters.noseLength if filters.noseLength else 0
        self.score.eyeShape = self.eyeShape - filters.eyeShape if filters.eyeShape else 0

        if filters.eyeColor:
            self.score.eyeColor = 0 if (
                self.eyeColor == filters.eyeColor) else 2
        else:
            self.score.eyeColor = 0
        if self.eyeDepth != 'deep':
            self.score.eyeColor += 1

        self.score.tail = 0
        if filters.tail and self.tail != filters.tail:
            self.score.tail = 1

        self.score.legs = 0
        if filters.legs and self.legs != filters.legs:
            self.score.legs = 1

        self.score.coat = 0 if catCoatDatasMatchTextureAndLength(
            self.coat, filters.coat) else 2
        self.score.color = 0 if catCoatDatasMatchColor(
            self.coat, filters.coat) else 2
