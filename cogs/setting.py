from calendar import c
import discord
from discord.ui import Select,View
from discord.ext import commands,tasks
from discord.commands import Option, SlashCommandGroup
import datetime
from lib.yamlutil import yaml
import copy
import lib.now as getTime
import math
import google.calendar as calendar
import main
import time

channelIdYaml = yaml(path='channelId.yaml')
channelId = channelIdYaml.load_yaml()

class SettingCog(commands.Cog):

    def __init__(self, bot):
        print('setting_initしたよ')
        self.bot = bot

    setting = SlashCommandGroup(
        name='setting', 
        description='test',        
        default_member_permissions=discord.Permissions(
            administrator=True,
            moderate_members=True
            )
        )

    @setting.command(name='channel', description='通知を送るチャンネルを指定します')
    async def set(self, ctx: discord.ApplicationContext,
                    channel: Option(discord.TextChannel, required=True,
                    description="通知を送るチャンネル")):
        
        channelId[ctx.guild.id] = {"channelid":channel.id,"guildname":ctx.guild.name,"channelname":channel.name}
        channelIdYaml.save_yaml(channelId)

        embed = discord.Embed(title="通知をこちらのチャンネルから送信します", color=0x1e90ff,
                description=f"サーバー名：{ctx.guild.name}\nチャンネル名：{channel.name}")
        channel = self.bot.get_partial_messageable(channel.id)
        await channel.send(embed=embed)
        await ctx.respond(content="設定しました。", ephemeral=True)
        print(f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nsetting_channel - set")

def setup(bot):
    bot.add_cog(SettingCog(bot))