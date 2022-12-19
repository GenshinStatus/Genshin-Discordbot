import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys
from lib.sql import Guild
import asyncio
import yaml_trans

bot = commands.Bot()
# debug_guilds=[879288794560471050]
print(type(sys.argv[1]))
load_dotenv()
TOKEN = os.getenv(f"TOKEN{str(sys.argv[1])}")

path = "./cogs"


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
        # traceback.format_exc())
        await bot.get_partial_messageable(1009731664412426240).send(error)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.respond(content="BOT管理者限定コマンドです", ephemeral=True)
    else:
        raise error


@bot.event
async def on_ready():
    print(f"Bot名:{bot.user} On ready!!")
    yaml_trans.init(bot.user.id)
    await guildsCount()


async def sendChannel(id) -> discord.PartialMessageable:
    channel: discord.PartialMessageable = bot.get_partial_messageable(id)
    return channel


async def guildsCount():
    Guild.set_guilds(bot.guilds)
    await asyncio.sleep(10)  # 複数のBOTを同時に再起動するときにちょっとあけとく
    count = Guild.get_count()
    await bot.change_presence(activity=discord.Game(name=f"厳選 Impactをプレイ中 / {count}サーバーで稼働中",))

bot.load_extensions(
    # 'cogs.wish_bata',
    # 'cogs.uidlist_bata',
    'cogs.genshin',
    'cogs.wish',
    'cogs.genbot',
    'cogs.uidlist',
    'cogs.artifact',
    'cogs.notification',
    'cogs.setting',
    'cogs.status',
    store=False
)

bot.run(TOKEN)
