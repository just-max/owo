from discord.ext import commands


# finally, clean code
encode,decode=lambda s:''.join(c//200*"🫂"+c%200//50*"💖"+c%50//10*"✨"+c%10//5*"🥺"+c%5*","+(c==0)*"❤️"+"👉👈"for c in s.encode()),lambda s:bytes([200*(c:=b.count)("🫂")+50*c("💖")+10*c("✨")+5*c("🥺")+c(",")for b in s.split("👉👈")[:-1]]).decode()
# courtesy of bottom software foundation: https://github.com/bottom-software-foundation/oneline-bottom-py


class Bottom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=["bowottom"])
    async def bottom(self, ctx, *, msg: str):
        await ctx.send(encode(msg))

    @commands.hybrid_command(aliases=["unbowottom"])
    async def unbottom(self, ctx, *, msg: str):
        await ctx.send(decode(msg))


def setup(bot):
    return bot.add_cog(Bottom(bot))
