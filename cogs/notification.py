import discord
from discord.ext import commands, tasks
from discord.commands import Option, SlashCommandGroup
from datetime import datetime, timedelta
import time
from model import notification


def datetime_to_unixtime(dt: datetime) -> int:
    """datetime型からunix時間をintで返します。

    Args:
        dt (datetime): datetime型の時間

    Returns:
        int: unix時間
    """
    return round(int(time.mktime(dt.timetuple())), -1)


class NotificationCog(commands.Cog):

    def __init__(self, bot: discord.Bot):
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
            channel = notification.get_notification_channel(ctx.guild_id)
        except ValueError as e:
            await ctx.respond(content="通知チャンネルが設定されていません。管理者に連絡して設定してもらってください。```/setting channel```で設定できます。")
            print(f"notification: channel: guild_id: {ctx.guild_id} -> 未登録")
            return

        # datetime型に直したほうが可読性が上がるので修正します
        plan_time = datetime.now() + timedelta(minutes=1280 - times - (resin*8))

        notification.add_notification(
            type_id=1,
            bot_id=ctx.bot.user.id,
            user_id=ctx.user.id,
            guild_id=ctx.guild_id,
            notification_time=plan_time
        )

        embed = discord.Embed(title=f"<t:{datetime_to_unixtime(plan_time)}:R>に通知を以下のチャンネルから送信します", color=0x1e90ff,
                              description=f"チャンネル：<#{channel}>")
        await ctx.respond(content="設定しました。", embed=embed)
        print(
            f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nnotification_resin - set")

    @tasks.loop(seconds=10)
    async def slow_count(self):
        notification_times, notification_channel_dict = notification.executing_notifications_search(
            self.bot.user.id)
        for notifi in notification_times:
            try:
                channel = await self.bot.get_channel(id=notification_channel_dict[notifi.guild_id])
                plan_time = datetime_to_unixtime(notifi.notification_time)
                embed = discord.Embed(title=f"樹脂通知", color=0x1e90ff,
                                      description=f"⚠あと約<t:{plan_time}:R>に樹脂が溢れます！")
                await channel.send(content=f"<@{notifi.user_id}>", embed=embed)
            except Exception as e:
                print(e)
                pass
        notification.delete_notifications(
            notification_ids=(v.notification_id for v in notification_times),
        )
        print("notification_resin - 通知")

    @slow_count.before_loop
    async def before_slow_count(self):
        print('waiting...')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(NotificationCog(bot))
