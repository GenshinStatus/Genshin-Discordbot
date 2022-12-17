import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from model import notification


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

        channel: discord.TextChannel = channel
        embed = discord.Embed(title="通知をこちらのチャンネルから送信します", color=0x1e90ff,
                              description=f"サーバー名：{ctx.guild.name}\nチャンネル名：{channel.name}")
        messageble_channel = self.bot.get_partial_messageable(channel.id)
        try:
            await messageble_channel.send(embed=embed)
        except discord.errors.Forbidden:
            embed = discord.Embed(title="⚠エラー", color=0x1e90ff,
                                  description=f"該当チャンネルではbotの権限が足りません。\nチャンネルの設定から、下記の画像のような項目で**botにメッセージを送信する権限が与えられているか**確認してください。")
            embed.add_field(name="必要な権限", value="チャンネルを見る、メッセージを送信")
            embed.add_field(name="権限不足のチャンネル", value=f"<#{channel.id}>")
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/1021082211618930801/1053331845724516402/image.png")
            await ctx.respond(embed=embed, ephemeral=True)
            print(
                f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nsetting_channel - Fordidden_set")
            return
        notification.set_notification_channel(ctx.guild_id, channel.id)
        await ctx.respond(content="設定しました。", ephemeral=True)
        print(
            f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nsetting_channel - set")


def setup(bot):
    bot.add_cog(SettingCog(bot))
