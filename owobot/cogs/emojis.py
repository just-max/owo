from __future__ import annotations

import re

from datetime import datetime, timezone, timedelta
import io
import tarfile
from pathlib import Path, PurePosixPath
import json
import codecs
from urllib.parse import urlparse

import discord
from discord.ext import commands
from discord.ext.commands import param

from owobot.misc import common

from typing import Iterable


_maybe_emoji_re = re.compile("<[^<>]*>")


def _buffer_tarinfo(name: str | Path, buffer: io.BytesIO, *, mtime: datetime = None) -> tarfile.TarInfo:
    result = tarfile.TarInfo(name=str(name))
    result.size = buffer.getbuffer().nbytes
    result.type = tarfile.REGTYPE
    result.mtime = (mtime if mtime is not None else datetime.now()).timestamp()
    return result


class Emojis(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_group()
    async def emoji(self, ctx: commands.Context):
        pass

    @emoji.command()
    @common.long_running_command
    async def archive(self, ctx: commands.Context):
        gz_buffer = io.BytesIO()
        index = {}
        with tarfile.open(mode="w:gz", fileobj=gz_buffer) as gz_file:
            for emoji in ctx.guild.emojis:
                emoji_buffer = io.BytesIO()
                await emoji.save(emoji_buffer, seek_begin=True)
                emoji_extension = PurePosixPath(urlparse(emoji.url).path).suffix
                emoji_friendly_name = f"{emoji.id}_{emoji.name}{emoji_extension}"
                gz_emoji_tarinfo = _buffer_tarinfo(f"data/{emoji_friendly_name}", emoji_buffer, mtime=emoji.created_at)
                gz_file.addfile(gz_emoji_tarinfo, emoji_buffer)

                index[emoji.id] = {
                    "name": emoji.name,
                    "data": emoji_friendly_name,
                    "animated": emoji.animated
                }

            index_buffer = io.BytesIO()
            json.dump(index, codecs.getwriter("utf-8")(index_buffer), indent=4)
            index_buffer.seek(0)
            gz_file.addfile(_buffer_tarinfo("index.json", index_buffer), fileobj=index_buffer)

        gz_buffer.seek(0)
        f = discord.File(gz_buffer, filename="emojis.tar.gz")
        await ctx.send(f"exported {len(index)} emojis!", file=f)

    @emoji.command()
    @commands.has_permissions(manage_emojis=True)
    @common.long_running_command
    async def stats(
            self, ctx: commands.Context,
            guild: discord.Guild = commands.CurrentGuild,
            after=param(
                converter=common.DatetimeConverter,
                default=lambda ctx: datetime.now(tz=timezone.utc) - timedelta(weeks=4)
            ),
            channel: discord.TextChannel = None,
            exclude: common.Annotated[Iterable[discord.TextChannel], commands.Greedy[discord.TextChannel]] = ()
    ):
        results = {em: 0 for em in guild.emojis}
        channels = set((channel, ) if channel is not None else guild.text_channels) - set(exclude)
        if not channels:
            await common.react_failure(ctx, "no channels to count emojis in")
            return
        for channel in channels:
            async for message in channel.history(after=after, limit=None):
                for match in _maybe_emoji_re.finditer(message.content):
                    try:
                        emoji = await commands.EmojiConverter().convert(ctx, match.group(0))
                        results[emoji] = results.get(emoji, 0) + 1
                    except commands.EmojiNotFound:
                        pass
                for reaction in message.reactions:
                    emoji = reaction.emoji
                    if isinstance(emoji, (discord.Emoji, discord.PartialEmoji)) and emoji.id is not None:
                        results[emoji] = results.get(emoji, 0) + reaction.count

        ranking = sorted(results.items(), key=lambda item: item[1], reverse=True)
        msg = "\n".join(
            f"{em if isinstance(em, discord.Emoji) and em.is_usable() else f'`{em.name}`'} {count}"
            for em, count in ranking
        )
        await common.send_paginated(ctx, msg if ranking else "no emojis found :<")


async def setup(bot: commands.Bot):
    await bot.add_cog(Emojis(bot))
