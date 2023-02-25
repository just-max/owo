import datetime
import io
import random
import re
import asyncio

import discord
import pandas as pd
import plotly.express as px
from discord.ext import commands

from owobot.misc import discord_emoji
from owobot.misc import common, owolib
from owobot.owobot import OwOBot


async def _1984(message: discord.Message):
    for name in ("one", "nine", "eight", "four"):
        await message.add_reaction(discord_emoji.get_unicode_emoji(name))


async def _buzzer(message: discord.Message):
    await message.reply("[𝐄𝐗𝐓𝐑𝐄𝐌𝐄𝐋𝐘 𝐋𝐎𝐔𝐃 𝐈𝐍𝐂𝐎𝐑𝐑𝐄𝐂𝐓 𝐁𝐔𝐙𝐙𝐄𝐑]")


class SimpleCommands(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot

    async def setup_hook(self):
        await self._add_app_commands()

    @commands.hybrid_command(name="obamamedal")
    async def obamamedal(self, ctx):
        await ctx.send(
            "https://media.discordapp.net/attachments/798609300955594782/816701722818117692/obama.jpg"
        )

    @commands.hybrid_command()
    async def owobamamedal(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/938102328282722345/939605208999264367/Unbenannt.png"
        )

    @commands.hybrid_command(aliases=["hewwo"])
    async def hello(self, ctx):
        await ctx.send(random.choice(["Hello", "Hello handsome :)"]))

    @commands.hybrid_command(aliases=["evewyone"])
    async def everyone(self, ctx):
        await ctx.send("@everyone")

    @commands.hybrid_command(brief="OwO")
    async def owo(self, ctx):
        await ctx.send(owolib.get_random_emote())

    @commands.hybrid_command(brief="gif nyaa~")
    async def dance(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/779413828051664966/944648168627372133/48561229-large.gif"
        )

    @commands.hybrid_command()
    async def gumo(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen einen GuMo!')}")

    @commands.hybrid_command()
    async def gumi(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen einen Guten Mittach!')}")

    @commands.hybrid_command()
    async def guna(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen eine GuNa!')}")

    @commands.hybrid_command()
    async def slap(self, ctx, member: discord.Member):
        name1 = common.get_nick_or_name(ctx.author)
        name2 = common.get_nick_or_name(member)
        await ctx.send(name1 + " slaps " + name2)
        await ctx.send("https://tenor.com/view/slap-bear-slap-me-you-gif-17942299")

    @commands.hybrid_command(brief="steal an avatar")
    async def steal(self, ctx, member: discord.Member):
        await ctx.send(member.display_avatar.url)

    @commands.hybrid_command(brief="see how many people are at the mensa")
    async def mensa(self, ctx):
        stats = (await self.bot.http_client.get("https://mensa.liste.party/api")).json()
        await ctx.send(
            f"Gerade wuscheln {stats['current']} Menschen in der Mensa. Das ist eine Auslastung von {stats['percent']:.0f}%")

    @commands.hybrid_command(brief="get a simple graph of the mensa usage")
    async def mensaplot(self, ctx, dayofweek: int = -1):
        if dayofweek == -1:
            dayofweek = datetime.datetime.today().weekday()
        df = pd.read_csv(self.bot.config.mensa_csv, names=["time", "count"], dtype={"time": float, "count": int})
        df['time'] = pd.to_datetime(df['time'], unit="s").dt.tz_localize('UTC').dt.tz_convert('Europe/Berlin')
        df = df.set_index("time")
        df = df.resample("1min").sum()
        df = df.loc[(df.index.dayofweek == dayofweek) & (df.index.hour > 9) & (df.index.hour < 16)]
        df["date"] = df.index.date
        df["clocktime"] = df.index.time
        dfw = df
        dfw.reset_index(drop=True, inplace=True)
        fig = px.line(dfw, x="clocktime", y="count", color="date")
        img = io.BytesIO()
        fig.write_image(img, format="png", scale=3)
        img.seek(0)
        await ctx.channel.send(file=discord.File(fp=img, filename="yeet.png"))

    @commands.hybrid_command(brief="Pong is a table tennis–themed twitch arcade sports video game "
                                   "featuring simple graphics.")
    async def ping(self, ctx: commands.Context):
        await ctx.send(f":ping_pong: ping pong! (`{round(self.bot.latency * 1000)}ms`)")

    @commands.hybrid_command(name="1984", brief="[redacted]")
    async def one_nine_eight_four(self, ctx: commands.Context):
        message = (
            ctx.message.reference.cached_message
            if ctx.message.reference
            else next((msg async for msg in ctx.channel.history(before=ctx.message, limit=1)), None)
        )

        if message is None:
            await common.react_failure(ctx, "no message to react to")
            return

        if not ctx.interaction:
            await ctx.message.delete()
        else:
            await ctx.reply("1984", mention_author=False, ephemeral=True)

        await _1984(message)

    sad_words = {"trauer", "schmerz", "leid"}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        word = message.content[1:].lower()
        if message.content and message.content[0] == self.bot.command_prefix and word in self.sad_words:
            self.bot.handle_dynamic(message)
            sad_words_minus = self.sad_words - {word}
            send_word = random.choice(tuple(sad_words_minus))
            await message.channel.send(send_word)

    _werben_pat = re.compile(r"\bwerben\b", re.IGNORECASE)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if not SimpleCommands._werben_pat.search(message.content):
            return
        await message.reply(
            "https://cdn.discordapp.com/attachments/937427217976262686/1047505652232228884/NBP5W2Z0e1.jpg"
        )

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def stroganoff(self, payload: discord.RawReactionActionEvent):
        if (
            not (payload.emoji.is_unicode_emoji() and payload.emoji.name == "🚨")  # new reaction is 🚨
            or payload.user_id == self.bot.user.id  # not from bot
        ):
            return

        msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        await _buzzer(msg)

    async def _add_app_commands(self):

        @self.bot.tree.context_menu(name="1984")
        async def one_nine_eight_four(interaction: discord.Interaction, message: discord.Message):
            await asyncio.gather(interaction.response.send_message("1984", ephemeral=True), _1984(message))

        @self.bot.tree.context_menu(name="Steal Avatar")
        async def steal(interaction: discord.Interaction, member: discord.Member):
            await interaction.response.send_message(member.display_avatar.url)

        @self.bot.tree.context_menu(name="🚨🚨🚨🚨🚨🚨🚨")
        async def steal(interaction: discord.Interaction, message: discord.Message):
            await asyncio.gather(interaction.response.send_message("🚨", ephemeral=True), _buzzer(message))


async def setup(bot: OwOBot):
    cog = SimpleCommands(bot)
    await cog.setup_hook()
    await bot.add_cog(cog)
