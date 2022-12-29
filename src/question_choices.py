from enum import Enum


def getChoiceInput(textToPrint, choices):
    receivedNumberInput = False
    choiceKeysArray = list(choices.keys())
    choiceValuesArray = list(choices.values())

    while not receivedNumberInput:

        choiceInput = input(f'''
{textToPrint}
{printChoices(choiceKeysArray)}
''')

        if not choiceInput:
            return None
        if choiceInput.isnumeric():
            receivedNumberInput = True

    return choiceValuesArray[int(choiceInput)]


def printChoices(choicesArray):
    output = ''
    for i in range(len(choicesArray)):
        output += f'{i + 1}. {choicesArray[i]}\n'
    return output
