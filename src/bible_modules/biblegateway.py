
import html
import logging
import re
from http.client import HTTPConnection

import aiohttp
from bs4 import BeautifulSoup

import bible_modules.bibleutils as bibleutils

HTTPConnection.debuglevel = 0

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


def remove_bible_title_in_search(string):
    return re.sub(r"<[^>]*>", "", string)


async def search(version, query):
    query = html.escape(query)

    url = f"https://www.biblegateway.com/quicksearch/?search={query}" + \
        f"&version={version}&searchtype=all&limit=50000&interface=print"

    search_results = {}
    length = 0

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp is not None:
                soup = BeautifulSoup(await resp.text(), "lxml")

                for row in soup.find_all(True, {"class": "row"}):
                    result = {}

                    for extra in row.find_all(True, {"class": "bible-item-extras"}):
                        extra.decompose()

                    result["title"] = row.find(True, {"class": "bible-item-title"})
                    result["text"] = row.find(True, {"class": "bible-item-text"})

                    if result["title"] is not None:
                        if result["text"] is not None:
                            result["title"] = result["title"].getText()
                            result["text"] = remove_bible_title_in_search(
                                bibleutils.purify_text(
                                    result["text"].get_text()[0:-1]))

                            length += 1
                            search_results["result" + str(length)] = result
            return search_results


async def get_result(query, version, headings, verse_numbers):
    query = query.replace("|", " ")

    url = f"https://www.biblegateway.com/passage/?search={query}&version={version}&interface=print"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp is not None:
                soup = BeautifulSoup(await resp.text(), "lxml")
                soup.prettify(formatter=lambda s: s.replace(u'\xa0', ' '))

                for div in soup.find_all("div", {"class": "result-text-style-normal"}):
                    text = ""
                    title = ""

                    if headings == "disable":
                        for heading in div.find_all("h3"):
                            heading.decompose()

                        for heading in div.find_all(True, {"class": "inline-h3"}):
                            heading.decompose()
                    else:
                        for heading in div.find_all("h3"):
                            title += f"{heading.get_text()} / "

                    for inline in div.find_all(True, {"class": "inline-h3"}):
                        inline.decompose()

                    for footnote in div.find_all(True, {"class": "footnotes"}):
                        footnote.decompose()

                    if verse_numbers == "disable":
                        for num in div.find_all(True, {"class": ["chapternum", "versenum"]}):  # noqa: E501
                            num.replace_with(" ")
                    else:
                        # turn chapter numbers into "1" otherwise the verse numbers
                        # look strange
                        for num in div.find_all(True, {"class": "chapternum"}):
                            num.replace_with("<**1**> ")

                        for num in div.find_all(True, {"class": "versenum"}):
                            num.replace_with(f"<**{num.text[0:-1]}**> ")

                    for meta in div.find_all(True, {"class": ["crossreference", "footnote"]}):  # noqa: E501
                        meta.decompose()

                    for paragraph in div.find_all("p"):
                        text += paragraph.get_text()

                    verse_object = {
                        "passage": div.find(True, {"class": "passage-display-bcv"}).string,  # noqa: E501
                        "version": div.find(True, {"class": "passage-display-version"}).string,  # noqa: E501
                        "title": title[0:-3],
                        "text": bibleutils.purify_text(text)
                    }

                    return verse_object
