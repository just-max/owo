import asyncio
import random
import pkgutil

import discord
from discord.ext import commands
from aiohttp import web

from owobot.owobot import OwOBot


_confession_html = pkgutil.get_data(__name__, "data/beichten.html").decode("utf-8")


class Beichten(commands.Cog):
    def __init__(self, bot: OwOBot, http_app: web.Application):
        super().__init__()
        self.bot = bot

        self._app = http_app
        self._add_routes()

    def _add_routes(self):
        self._app.add_routes((
            web.get(
                "/beichten",
                self._confession_form,
            ),
            web.post(
                "/api/v0/confession",
                self._handle_confession,
            ),
        ))

    async def _confession_form(self, request: web.Request):
        return web.Response(text=_confession_html, content_type="text/html")

    async def _handle_confession(self, request: web.Request):
        params = await request.post()

        channel_id_s = params.get("channel", None)
        message = params.get("message", None)

        if channel_id_s is None or message is None:
            raise web.HTTPUnprocessableEntity(text="'channel' and 'message' parameters are required\n")

        try:
            if len(channel_id_s) > 32:  # protect against DoS, actual maximum length is 18
                raise ValueError
            channel_id = int(channel_id_s)
        except ValueError:
            raise web.HTTPBadRequest(text="'channel' must be an int\n")

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            raise web.HTTPNotFound(text="no channel found with given id\n")

        if len(message) > 5000:
            raise web.HTTPBadRequest(text="message is too long\n")

        await self._beichten(channel, message)

        return web.Response(text="confessed.")

    async def _beichten(self, channel: discord.abc.Messageable, message: str):
        embed = discord.Embed(description=message)
        embed.set_author(
            name="Beichtstuhl",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/"
                     "St.leonhard-ffm-beichtstuhl001.jpg/647px-St.leonhard-ffm-beichtstuhl001.jpg"
        )
        await channel.send(embed=embed)

    @commands.hybrid_command(brief="für dumme gedanken")
    async def beichten(self, ctx: commands.Context, message: str):
        if ctx.interaction is None:
            await asyncio.gather(
                ctx.channel.send("use `/beichten <message>` to retain your privacy"),
                ctx.message.delete(),
            )
            return

        delay = 60 * random.uniform(1, 3)
        ctx.interaction.response.send_message(
            f"the priest will respect your privacy; please wait {delay} seconds",
            ephemeral=True,
        )
        await asyncio.sleep(delay)
        await self._beichten(ctx.channel, message)


def setup(bot: OwOBot):
    return bot.add_cog(Beichten(bot, http_app=bot.http_app))
