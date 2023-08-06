"""
Copyright (c) 2022 Philipp Scheer
"""


import os
import logging


baseUrl = "https://api.friday.fipsi.at/v1"
logger = logging.getLogger("rockeet")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.WARNING)


def setToken(newToken: str):
    logger.debug(f"setting token to {newToken[:15]}xxx")
    os.environ["ROCKEET_TOKEN"] = newToken

def getToken():
    return os.environ["ROCKEET_TOKEN"]

def setLoggingLevel(level: int):
    logger.setLevel(level)


from . import File
from . import Image
from . import Audio
from . import Video
from . import Session