
import re

import aiohttp
from bs4 import BeautifulSoup


def remove_html(text):
    return re.sub(r"<[^<]+?>", "", text)


def purify_text(text):
    result = text.replace("“", "\"")
    result = result.replace("[", " <")
    result = result.replace("]", "> ")
    result = result.replace("”", "\"")
    result = result.replace("‘", "'")
    result = result.replace("’", "'")
    result = result.replace(",", ", ")
    result = result.replace(".", ". ")
    result = result.replace(". \"", ".\"")
    result = result.replace(". '", ".'")
    result = result.replace(" .", ".")
    result = result.replace(", \"", ",\"")
    result = result.replace(", '", ",'")
    result = result.replace("!", "! ")
    result = result.replace("! \"", "!\"")
    result = result.replace("! '", "!'")
    result = result.replace("?", "? ")
    result = result.replace("? \"", "?\"")
    result = result.replace("? '", "?'")
    result = result.replace(":", ": ")
    result = result.replace(";", "; ")
    result = result.replace("¶ ", "")
    result = result.replace("â", "\"") 
    result = result.replace(" â", "\"") 
    result = result.replace("â", "-") 
    return re.sub(r"\s+", " ", result)


async def get_random_verse():
    url = "https://dailyverses.net/random-bible-verse"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp is not None:
                soup = BeautifulSoup(await resp.text(), "lxml")
                verse = soup.find(
                    "div", {"class": "bibleChapter"}).find("a").get_text()

                return verse


async def get_votd():
    url = "https://www.biblegateway.com/reading-plans/verse-of-the-day/next"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp is not None:
                soup = BeautifulSoup(await resp.text(), "lxml")
                verse = soup.find(True, {"class": "rp-passage-display"}).get_text()

                return verse
