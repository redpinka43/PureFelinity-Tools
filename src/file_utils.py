import os


def createDirectory(path: str):
    directoryExists = os.path.exists(path)
    if not directoryExists:
        os.makedirs(path)
