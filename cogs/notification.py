import discord
from discord.ui import Select, View
from discord.ext import commands, tasks
from discord.commands import Option, SlashCommandGroup
from datetime import datetime, timedelta
from lib.yamlutil import yaml
import time

channelIdYaml = yaml(path='channelId.yaml')
channelId = channelIdYaml.load_yaml()
notificationYaml = yaml(path='notification.yaml')
notificationData = notificationYaml.load_yaml()


def datetime_to_unixtime(dt: datetime) -> int:
    """datetime型からunix時間をintで返します。

    Args:
        dt (datetime): datetime型の時間

    Returns:
        int: unix時間
    """
    return round(int(time.mktime(dt.timetuple())), -1)


class NotificationCog(commands.Cog):

    def __init__(self, bot):
        print('Notification_initしたよ')
        self.bot = bot
        self.slow_count.start()

    notification = SlashCommandGroup('notification', 'test')

    @notification.command(name='resin', description='樹脂が160になる前に通知します')
    async def resin(self, ctx: discord.ApplicationContext,
                    resin: Option(int,
                                  required=True,
                                  description="現在の樹脂量",
                                  max_value=160,
                                  min_value=1),
                    times: Option(int,
                                  required=False,
                                  description="溢れる何分前に通知するか（未設定の場合は40分前）",
                                  max_value=180,
                                  min_value=1,
                                  default=40)):
        await ctx.response.defer(ephemeral=True)  # deferのほうが良さそうなのでこっちに変更したい
        try:
            channelIdYaml = yaml(path='channelId.yaml')
            channelId = channelIdYaml.load_yaml()
            print(channelId[ctx.guild.id])
        except:
            await ctx.respond(content="通知チャンネルが設定されていません。管理者に連絡して設定してもらってください。```/setting channel```で設定できます。")
            return

        # datetime型に直したほうが可読性が上がるので修正します
        plan_time = datetime_to_unixtime(
            datetime.now() + timedelta(minutes=1280 - times - (resin*8)))

        # 以下をSQLに変更します！
        notificationData[plan_time] = {"userId": f"<@{ctx.author.id}>",
                                       "channelId": channelId[ctx.guild.id]['channelid'], "time": times}
        notificationYaml.save_yaml(notificationData)

        embed = discord.Embed(title=f"<t:{plan_time}:R>に通知を以下のチャンネルから送信します", color=0x1e90ff,
                              description=f"チャンネル：<#{channelId[ctx.guild.id]['channelid']}>")
        await ctx.respond(content="設定しました。", embed=embed)
        print(
            f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nnotification_resin - set")

    @tasks.loop(seconds=10)
    async def slow_count(self):
        # ここもSQLに変更します
        notificationYaml = yaml(path='notification.yaml')
        notificationData = notificationYaml.load_yaml()
        try:
            plan_time = notificationData[round(round(time.time()), -1)]
            channel = self.bot.get_partial_messageable(plan_time["channelId"])

            huga = round(round(time.time()), -1) + plan_time['time'] * 60

            embed = discord.Embed(title=f"樹脂{plan_time['time']}分前通知", color=0x1e90ff,
                                  description=f"⚠あと約<t:{huga}:R>に樹脂が溢れます！")
            await channel.send(content=f"{plan_time['userId']}", embed=embed)
            notificationData.pop(round(round(time.time()), -1))
            notificationYaml.save_yaml(notificationData)
            print(f"notification_resin - 通知")
        except:
            return


def setup(bot):
    bot.add_cog(NotificationCog(bot))
