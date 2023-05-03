import discord
from discord.ext import commands, tasks
from lib.sql import Guild


class Time(commands.Cog):

    def __init__(self, bot: discord.AutoShardedBot):
        print('Status_init')
        self.bot = bot
        self.slow_count.start()

    @tasks.loop(minutes=5)
    async def slow_count(self):
        bot = self.bot
        Guild.set_guilds(bot.guilds)
        count = Guild.get_count()
        await bot.change_presence(activity=discord.Game(name=f"厳選 Impactをプレイ中 / {count}サーバーで稼働中",))

    @slow_count.before_loop
    async def before(self):
        print("waiting")
        await self.bot.wait_until_ready()


def setup(bot: discord.AutoShardedBot):
    bot.add_cog(Time(bot))
