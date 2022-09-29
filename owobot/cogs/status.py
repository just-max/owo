from discord.ext import commands
from aiohttp import web

from owobot.owobot import OwOBot


class Status(commands.Cog):
    def __init__(self, bot: commands.Bot, http_app: web.Application):
        super().__init__()
        self.bot = bot

        self._app = http_app
        self._add_routes()

    def _add_routes(self):
        self._app.add_routes((web.get("/status", self._status),))

    async def _status(self, request: web.Request):
        return web.Response(
            text="200 OK.\n"
            "Loaded cogs:\n"
            + "\n".join(sorted(self.bot.extensions.keys()))
        )


def setup(bot: OwOBot):
    return bot.add_cog(Status(bot, http_app=bot.http_app))
