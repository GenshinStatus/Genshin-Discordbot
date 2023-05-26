import discord
from discord.ext import commands
import os
from lib import sql
import asyncio
import yaml_trans


intents = discord.Intents.default()
intents.guilds = True
bot = commands.AutoShardedBot(intents=intents)
# debug_guilds=[879288794560471050]
TOKEN = os.getenv(f"TOKEN")

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
async def on_guild_join(guild: discord.Guild):
    sql.Ephemeral.init_ephemeral(guild.id)

@bot.event
async def on_ready():
    print(f"Bot名:{bot.user} On ready!!")
    yaml_trans.init(bot.user.id)
    await guildsCount()


async def sendChannel(id) -> discord.PartialMessageable:
    channel: discord.PartialMessageable = bot.get_partial_messageable(id)
    return channel


async def guildsCount():
    sql.Guild.set_guilds(bot.guilds)
    await asyncio.sleep(10)  # 複数のBOTを同時に再起動するときにちょっとあけとく
    count = sql.Guild.get_count()
    await bot.change_presence(activity=discord.Game(name=f"厳選 Impactをプレイ中 / {count}サーバーで稼働中(累計)",))

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
