
import logging
import os
import sys
import configparser
from http.client import HTTPConnection

import aiohttp
from bs4 import BeautifulSoup

import bible_modules.bibleutils as bibleutils

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f"{dir_path}/..")

import central  # noqa: E402

config = configparser.ConfigParser()
config.read(f"{dir_path}/../config.ini")

HTTPConnection.debuglevel = 0

logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

versions = {
    "KJVA": "de4e12af7f28f599-01",
}

version_names = {
    "KJVA": "King James Version with Apocrypha (KJVA)",
}


async def get_result(query, ver, headings, verse_numbers):
    query = query.replace("|", " ")

    url = f"https://api.scripture.api.bible/v1/bibles/{versions[ver]}/search"
    headers = {"api-key": config["apis"]["apibible"]}
    params = {"query": query, "limit": "1"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            if resp is not None:
                data = await resp.json()
                data = data["data"]["passages"]
                text = None

                if data[0]["bibleId"] != versions[ver]:
                    central.log_message("err", 0, "apibible", "global",
                                        f"{version} is no longer able to be used.")
                    return

                if len(data) > 0:
                    text = data[0]["content"]

                if text is None:
                    return

                soup = BeautifulSoup(text, "lxml")

                title = ""
                text = ""

                for heading in soup.find_all("h3"):
                    title += f"{heading.get_text()} / "
                    heading.decompose()

                for span in soup.find_all("span", {"class": "v"}):
                    if verse_numbers == "enable":
                        span.replace_with(f"<**{span.get_text()}**> ")
                    else:
                        span.replace_with(" ")

                    span.decompose()

                for p in soup.find_all("p", {"class": "p"}):
                    text += p.get_text()

                if headings == "disable":
                    title = ""

                text = f" {bibleutils.purify_text(text).rstrip()}"

                verse_object = {
                    "passage": query,
                    "version": version_names[ver],
                    "title": title[0:-3],
                    "text": text
                }

                return verse_object
