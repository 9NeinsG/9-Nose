import configparser
import math
import os
import time

import tinydb

from data import languages
from extensions.vylogger import VyLogger

dir_path = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(f"{dir_path}/config.ini")

configVersion = configparser.ConfigParser()
configVersion.read(f"{dir_path}/config.example.ini")

version = configVersion["meta"]["version"]
icon = "https://cdn.discordapp.com/app-icons/681455136316325928/8ffda80ccfca35f7d27f04bab61b7f4b.png"  # noqa: E501
cmd_prefix = config["BertrandComparet"]["commandPrefix"]

logger = VyLogger("default")

db = tinydb.TinyDB(f"{dir_path}/../databases/db")
guildDB = tinydb.TinyDB(f"{dir_path}/../databases/guilddb")
versionDB = tinydb.TinyDB(f"{dir_path}/../databases/versiondb")
optoutDB = tinydb.TinyDB(f"{dir_path}/../databases/optoutdb")

languages = languages

brackets = {
    "first": config["BertrandComparet"]["dividingBrackets"][0],
    "second": config["BertrandComparet"]["dividingBrackets"][1]
}


def capitalize_first_letter(string):
    return string[0].upper() + string[1:]


def halve_string(s):

    middle = math.floor(len(s) / 2)
    before = s.rfind(" ", middle)
    after = s.index(" ", middle + 1)

    if (middle - before) < (after - middle):
        middle = after
    else:
        middle = before

    return {
        "first": s[0:middle],
        "second": s[middle + 1:]
    }


def log_message(level, shard, sender, source, msg):
    message = f"[shard {str(shard)}] <{sender}@{source}> {msg}"

    if level == "warn":
        logger.warning(message)
    elif level == "err":
        logger.error(message)
    elif level == "info":
        logger.info(message)
    elif level == "debug":
        logger.debug(message)


def get_raw_language(obj):
    try:
        return getattr(languages, obj).raw_object
    except AttributeError:
        return getattr(languages, "english").raw_object


def add_optout(entryid):
    ideal_entry = tinydb.Query()
    result = optoutDB.search(ideal_entry.id == entryid)

    if len(result) > 0:
        return False
    else:
        db.remove(ideal_entry.id == entryid)
        guildDB.remove(ideal_entry.id == entryid)

        optoutDB.insert({"id": entryid})
        return True


def remove_optout(entryid):
    ideal_entry = tinydb.Query()
    result = optoutDB.search(ideal_entry.id == entryid)

    if len(result) > 0:
        optoutDB.remove(ideal_entry.id == entryid)
        return True
    else:
        return False


def is_optout(entryid):
    ideal_entry = tinydb.Query()
    result = optoutDB.search(ideal_entry.id == entryid)

    if len(result) > 0:
        return True
    else:
        return False


def is_snowflake(snowflake):
    if isinstance(snowflake, int):
        if snowflake > 1.4200704e+16:
            return True
    else:
        try:
            if isinstance(int(snowflake), int):
                if int(snowflake) > 1.4200704e+16:
                    return True
        except ValueError:
            return False
