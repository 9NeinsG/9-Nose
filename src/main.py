import os
import os.path
from os import listdir
import sys
import discord
from discord import opus
import asyncio
import configparser
import random
import time
import re
import requests
import textwrap
import traceback
import ndjson
import numpy
from io import BytesIO

from name_scraper import client as name_scraper
from handlers.logic.settings import languages
from handlers.commands import CommandHandler
from handlers.verses import VerseHandler
from extensions import bot_extensions, compile_extrabiblical

from PIL import ImageFont, ImageDraw, Image

from gtts import gTTS
from discord.ext import commands
from textblob import TextBlob

import central
#import comparet
#import shippost
from bulli import bulli

dir_path = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(f"{dir_path}/config.ini")

configVersion = configparser.ConfigParser()
configVersion.read(f"{dir_path}/config.example.ini")

client = discord.AutoShardedClient()

discord.opus.load_opus

memes = []
pullingCSV = False
commandlist = ["help", "refresh", "speak", "nospeak", "status", "dc", "bw", "servers", "nobulli", "echo"]
pic_ext = ['.jpg', '.png', '.jpeg', 'gif']
#musicfiles = listdir('sound')
#cooldown = time.time()-15
cooldowns = {}


async def send(words):
    channel = client.get_channel(624891515906293760)
    await channel.send(words)


class BertrandComparet(discord.AutoShardedClient):
    def __init__(self, *args, loop=None, **kwargs):
        super().__init__(*args, loop=loop, **kwargs)

        self.bg_task = self.loop.create_task(bot_extensions.run_timed_votds(self))
        self.load_names = self.loop.create_task(name_scraper.update_books(config["apis"]["apibible"]))
        self.current_page = None
        self.total_pages = None

    async def on_ready(self):
        if int(config["BertrandComparet"]["shards"]) < 2:
            status = f"=help"
            activity = discord.Game(status)

            await self.change_presence(status=discord.Status.online, activity=activity)

            central.log_message("info", 1, "global", "global", "connected")

        await bot_extensions.send_server_count(self)

    async def on_shard_ready(self, shard_id):
        shard_count = str(config["BertrandComparet"]["shards"])
        s_id = str(shard_id + 1)
        status = f"Bible"

        activity = discord.Game(status)
        await self.change_presence(status=discord.Status.online, activity=activity, shard_id=shard_id)

        central.log_message("info", shard_id + 1, "global", "global", "shard connected")

    async def on_guild_join(self, guild):
        await bot_extensions.send_server_count(self)

    async def on_guild_remove(self, guild):
        await bot_extensions.send_server_count(self)

    @client.event
    async def on_message(self, raw):
        global cooldown
        global musicfiles
        global yggdrasilcmd
        global commandlist
        global memes
        global memebox
        global pic_ext
        global pullingCSV
        owner_id = config["BertrandComparet"]["owner"]
        await self.wait_until_ready()

        if(raw.content and len(raw.content) < 200):
            await bulli(raw)

        if ":" not in raw.content:
            if config["BertrandComparet"]["commandPrefix"] not in raw.content:
                return

        ctx = {
            "self": bot,
            "author": raw.author,
            "identifier": f"{raw.author.id}",
            "channel": raw.channel,
            "message": raw.content,
            "raw": raw,
            "guild": None,
            "language": None
        }

        is_self = ctx["author"] == self.user
        is_optout = central.is_optout(str(ctx["author"].id))
        if is_self or is_optout:
            return

        is_owner = ctx["identifier"] == owner_id
        if is_owner:
            ctx["identifier"] = "owner"

        language = languages.get_language(ctx["author"])

        if hasattr(ctx["channel"], "guild"):
            ctx["guild"] = ctx["channel"].guild

            if language is None:
                language = languages.get_guild_language(ctx["guild"])

            guild_id = str(ctx["channel"].guild.id)
            chan_id = str(ctx["channel"].id)

            source = f"{guild_id}#{chan_id}"

            if "Discord Bot" in ctx["channel"].guild.name:
                if not is_owner:
                    return
        else:
            source = "unknown (direct messages?)"

        if ctx["guild"] is None:
            shard = 1
        else:
            shard = ctx["guild"].shard_id + 1

        if language is None or language in ["english_us", "english_uk"]:
            language = "english"

        if config["BertrandComparet"]["devMode"] == "True":
            # more often than not, new things are added that aren't filtered

            language = "default"

            if not is_owner:
                return

        embed_or_reaction_not_allowed = False

        if ctx["guild"] is not None:
            try:
                perms = ctx["channel"].permissions_for(ctx["guild"].me)

                if perms is not None:
                    if not perms.send_messages or not perms.read_messages:
                        return

                    if not perms.embed_links:
                        embed_or_reaction_not_allowed = True

                    if not perms.add_reactions:
                        embed_or_reaction_not_allowed = True

                    no_managing = not perms.manage_messages
                    no_history = not perms.read_message_history

                    if no_managing or no_history:
                        embed_or_reaction_not_allowed = True
            except AttributeError:
                pass

        ctx["language"] = central.get_raw_language(language)

        if ctx["message"].startswith(config["BertrandComparet"]["commandPrefix"]):
            command = ctx["message"][1:].split(" ")[0]
            remainder = " ".join(ctx["message"].split(" ")[1:])

            cmd_handler = CommandHandler()

            res = await cmd_handler.process_command(ctx, command, remainder)

            original_command = ""
            self.current_page = 1

            if res is None:
                return

            if "announcement" in res:
                await bot_extensions.send_announcement(ctx, res)
                return

            if "isError" not in res:
                if embed_or_reaction_not_allowed:
                    ch = ctx["channel"]

                    await ch.send("Permissions are not properly configured.")
                    await ch.send("Please check https://NineNeins.com for more information.")
                    return

                if "twoMessages" in res:
                    await ctx["channel"].send(res["firstMessage"])
                    await ctx["channel"].send(res["secondMessage"])
                elif "paged" in res:
                    self.total_pages = len(res["pages"])

                    msg = await ctx["channel"].send(embed=res["pages"][0])

                    await msg.add_reaction("⬅")
                    await msg.add_reaction("➡")

                    def check(r, u):
                        if r.message.id == msg.id:
                            if str(r.emoji) == "⬅":
                                if u.id != bot.user.id:
                                    if self.current_page != 1:
                                        self.current_page -= 1
                                        return True
                            elif str(r.emoji) == "➡":
                                if u.id != bot.user.id:
                                    if self.current_page != self.total_pages:
                                        self.current_page += 1
                                        return True

                    continue_paging = True

                    try:
                        while continue_paging:
                            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                            await reaction.message.edit(embed=res["pages"][self.current_page - 1])

                            reaction, user = await bot.wait_for('reaction_remove', timeout=60.0, check=check)
                            await reaction.message.edit(embed=res["pages"][self.current_page - 1])
                    except (asyncio.TimeoutError, IndexError):
                        try:
                            await msg.clear_reactions()
                        except (discord.errors.Forbidden, discord.errors.NotFound):
                            pass
                elif "embed" in res:
                    await ctx["channel"].send(embed=res["embed"])
                else:
                    if "reference" not in res and "text" not in res:
                        await ctx["channel"].send(embed=res["message"])
                    else:
                        await ctx["channel"].send(res["message"])

                lang = central.get_raw_language(language)
                for original_command_name in lang["commands"].keys():
                    untranslated = ["setlanguage", "userid", "ban", "unban",
                                    "reason", "optout", "unoptout", "eval",
                                    "jepekula", "joseph", "tiger", "rose",
                                    "lsc", "heidelberg", "ccc"]

                    if lang["commands"][original_command_name] == command:
                        original_command = original_command_name
                    elif command in untranslated:
                        original_command = command

                clean_args = remainder.replace("\"", "").replace("'", "").replace("  ", " ")
                clean_args = clean_args.replace("\n", "").strip()

                ignore_arg_commands = ["puppet", "eval", "announce"]

                if original_command in ignore_arg_commands:
                    clean_args = ""

                central.log_message(res["level"], shard, ctx["identifier"], source, f"+{original_command} {clean_args}")
            else:
                await ctx["channel"].send(embed=res["message"])
        else:
            verse_handler = VerseHandler()

            result = await verse_handler.process_raw_message(raw, ctx["author"], ctx["language"], ctx["guild"])

            if result is not None:
                if embed_or_reaction_not_allowed:
                    ch = ctx["channel"]

                    await ch.send("Permissions are not properly configured.")
                    await ch.send("Please check https://NineNeins.com for more information.")
                    return

                if "invalid" not in result and "spam" not in result:
                    for item in result:
                        try:
                            if "twoMessages" in item:
                                await ctx["channel"].send(item["firstMessage"])
                                await ctx["channel"].send(item["secondMessage"])
                            elif "message" in item:
                                await ctx["channel"].send(item["message"])
                            elif "embed" in item:
                                await ctx["channel"].send(embed=item["embed"])

                            if "reference" in item:
                                central.log_message(item["level"], shard, ctx["identifier"], source, item["reference"])
                        except (KeyError, TypeError):
                            pass
                elif "spam" in result:
                    central.log_message("warn", shard,
                                        ctx["identifier"], source,
                                        "Too many verses at once.")
                    await ctx["channel"].send(result["spam"])


if int(config["BertrandComparet"]["shards"]) > 1:
    bot = BertrandComparet(shard_count=int(config["BertrandComparet"]["shards"]))
else:
    bot = BertrandComparet()

if config["BertrandComparet"]["devMode"] == "True":
    compile_extrabiblical.compile_resources()

central.log_message("info", 0, "global", "global",
                    f"(Bertrand)Comparte {central.version} by GreyingError")
bot.run(config["BertrandComparet"]["token"], reconnect=True)
