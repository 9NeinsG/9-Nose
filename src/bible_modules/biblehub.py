
import logging
from http.client import HTTPConnection

import aiohttp
from bs4 import BeautifulSoup

import bible_modules.bibleutils as bibleutils

HTTPConnection.debuglevel = 0

logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

version_names = {
    "BSB": "Berean Study Bible (BSB)",
    "NHEB": "New Heart Study Bible (NHEB)",
    "WBT": "Webster's Bible Translation (WBT)"
}


async def get_result(query, version, verse_numbers):
    if "|" in query:
        book = query.split("|")[0]
        chapter = query.split("|")[1].split(":")[0]
        starting_verse = query.split("|")[1].split(":")[1]
        ending_verse = starting_verse
    else:
        book = " ".join(query.split(" ")[:-1])
        chapter = query.split(" ")[-1].split(":")[0]
        starting_verse = query.split(" ")[-1].split(":")[1]
        ending_verse = starting_verse

    if "-" in starting_verse:
        temp = starting_verse.split("-")

        if len(temp[1]) != 0:
            starting_verse = temp[0]
            ending_verse = temp[1]
        else:
            starting_verse = temp[0]
            ending_verse = "-"

    url = f"http://biblehub.com/{version.lower()}/{book.lower()}/{chapter}.htm"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            soup = BeautifulSoup(await resp.text(), "lxml")

            for div in soup.find_all("div", {"class": "chap"}):
                for p in div.find_all("p", {"class": "cross"}):
                    p.decompose()

                for heading in div.find_all("p", {"class": "hdg"}):
                    heading.decompose()

                if ending_verse == "-":
                    ending_verse = div.find_all(
                        "span", {"class": "reftext"})[-1].get_text()

                for sup in div.find_all("span", {"class": "reftext"}):
                    if verse_numbers == "enable":
                        sup.replace_with(f"<**{sup.get_text()}**> ")
                    else:
                        sup.replace_with(" ")

                text = div.get_text()

                text = text.split(f"<**{int(ending_verse) + 1}**>")[0]

                if int(starting_verse) != 1:
                    text = f" <**{starting_verse}**>" + text.split(
                        f"<**{int(starting_verse)}**>")[1]

                if text is None:
                    return

                verse_object = {
                    "passage": query.replace("|", " "),
                    "version": version_names[version],
                    "title": "",
                    "text": bibleutils.purify_text(text)
                }

                return verse_object
