import logging

import httpx

from discord.ext import commands

from owobot.owobot import OwOBot
from owobot.misc import common


log = logging.getLogger(__name__)


_OPENAI_CHAT_ROLES = ("system", "user", "assistant")


class OpenAIError(Exception):
    pass


class BearerAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        request.headers["authorization"] = "Bearer " + self.token
        yield request


class Oracle(commands.Cog):
    def __init__(self, bot: OwOBot):
        super().__init__()
        self.bot = bot

        self.http_client = httpx.AsyncClient(
            auth=BearerAuth(self.bot.config.openai_token),
            follow_redirects=True,
            headers={"Content-Type": "application/json"},
            timeout=None,  # OpenAI might take a while to respond
        )

        self.prompt_messages = tuple(
            dict(role=role, content=content)
            for role, content in
            (tuple(tok.strip() for tok in prompt.split(":", maxsplit=1)) for prompt in self.bot.config.oracle_prompt)
        )

        for msg in self.prompt_messages:
            if msg["role"] not in _OPENAI_CHAT_ROLES:
                raise ValueError(f"invalid role: {msg['role']} (must be one of {', '.join(_OPENAI_CHAT_ROLES)})")

    @commands.hybrid_command(brief="ask the gods for advice (cw: ai generated content)")
    @common.long_running_command
    async def oracle(self, ctx: commands.Context, request: str):
        # response = await self.http_client.post
        response = (await self.http_client.post(
            "https://api.openai.com/v1/chat/completions",
            json=dict(
                model="gpt-3.5-turbo",
                temperature=0.7,
                messages=(
                    self.prompt_messages
                    + (dict(role="user", content=request), )
                )
            )
        )).json()

        if "error" in response:
            raise OpenAIError(response["error"])

        await ctx.send(response["choices"][0]["message"]["content"])


async def setup(bot: OwOBot):
    # if token is empty string, don't add cog
    if bot.config.openai_token:
        await bot.add_cog(Oracle(bot))
