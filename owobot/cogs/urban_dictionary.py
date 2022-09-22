from __future__ import annotations

import codecs
import io
import itertools as it
import json
from pprint import pformat, pprint
import urllib
from urllib.parse import urlparse, urlencode, ParseResult as UrlParseResult
from pathlib import PurePosixPath as P
import re
import random

from owobot.misc import common
from owobot.owobot import OwOBot
from owobot.misc import owolib

import httpx
import discord
from discord.ext import commands
from discord.ext.commands import Cog, Context, Bot
from discord.utils import escape_markdown

from typing import Union

_UD_URL = httpx.URL("https://www.urbandictionary.com")


def _ud_def_url(term, defid=None, ud_url=_UD_URL):
    return (
        ud_url
        .copy_with(path="/define.php")
        .copy_merge_params(common.nullable_dict(term=term, defid=defid))
    )


def _ud_author_url(author, ud_url=_UD_URL):
    return (
        ud_url
        .copy_with(path="/author.php")
        .copy_merge_params(dict(author=author))
    )


_UD_DEF_LINK_PAT = re.compile(r"\[ (?P<term> [^\[\]]* ) \]", re.VERBOSE)


def _linkify(text, max_length):
    return common.ellipsize_sub(
        _UD_DEF_LINK_PAT,
        lambda m: f"[{m.group('term')}]({_ud_def_url(m.group('term'))})",
        text,
        max_length,
        safe_replacement=r"\g<term>"
    )


def _ud_embed(definition):
    embed = discord.Embed(
        type="rich",
        title=common.ellipsize(definition["word"], 256),
        url=_ud_def_url(term=definition["word"], defid=definition["defid"]),
        colour=0xE86222
    )
    embed.set_author(
        name=common.ellipsize(definition["author"], 256),
        url=_ud_author_url(definition["author"]),
    )
    embed.description = _linkify(
        escape_markdown(definition["definition"])
        + "\n\n*"
        + escape_markdown(definition["example"])
        + "*",
        min(6000 - len(embed), 4096)
    )
    return embed


class UrbanDictionary(Cog):
    def __init__(self,
                 bot: Bot,
                 http_client: httpx.AsyncClient = None,
                 api_url: httpx.URL = httpx.URL("https://api.urbandictionary.com/v0")):
        super().__init__()
        self.bot = bot
        self.http_client = http_client or httpx.AsyncClient()
        self.api_url = api_url

    async def api_get(self, path: Union[str, P], **kwargs):
        return await self.http_client.get(self.api_url.copy_with(path=str(P(self.api_url.path) / path)), **kwargs)

    @commands.hybrid_group()
    async def ud(self, ctx: Context):
        pass

    @ud.command(brief="randomly show the definition of a word from Urban Dictionary")
    @common.long_running_command
    async def random(self, ctx: Context):
        result = (await self.api_get(P("random"))).json()
        await ctx.send(embed=_ud_embed((result["list"][0])))

    @ud.command(brief="look up the definition of a term from Urban Dictionary")
    @common.long_running_command
    async def define(self, ctx: Context, term: str):
        result = (await self.api_get(P("define"), params=dict(term=term))).json()
        if rl := result["list"]:
            await ctx.send(embed=_ud_embed(rl[0]))
        else:
            await common.react_empty(ctx, "no definition found")


def setup(bot: OwOBot):
    return bot.add_cog(UrbanDictionary(bot, http_client=bot.http_client))
