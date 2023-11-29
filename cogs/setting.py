import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup, OptionChoice
from model import notification
import lib.sql as sql

SELECT_EQHEMERAL = [
    OptionChoice(name='他人への表示をオンにする', value=1),
    OptionChoice(name='他人への表示をオフにする', value=0)
]

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
                url="https://genshin-cdn.cinnamon.works/notify/no_permission.jpg")
            await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
            print(
                f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nsetting_channel - Fordidden_set")
            return
        notification.set_notification_channel(ctx.guild_id, channel.id)
        await ctx.respond(content="設定しました。", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
        print(
            f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nsetting_channel - set")

    @setting.command(name='ephemeral', description='コマンドの使用が他人に表示するか設定できます。')
    async def set(self, 
        ctx: discord.ApplicationContext,
        is_ephemeral_option: Option(int, name="コマンド履歴について", choices=SELECT_EQHEMERAL, required=True, description="ビルド画像など、自分が使ったコマンドの履歴を他人が見れるようにするか切り替えます。")):

        try:
            print(is_ephemeral_option)
            if is_ephemeral_option == 1:
               sql.Ephemeral.set_ephemeral(ctx.guild_id, False)
            else:
                sql.Ephemeral.set_ephemeral(ctx.guild_id, True)
        except discord.errors.Forbidden:
            embed = discord.Embed(title="⚠エラー", color=0x1e90ff,
                                  description=f"何らかのエラーで失敗しました。")
            await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
            return
        try:
            await ctx.respond(content="設定しました。", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
        except:
            sql.Ephemeral.init_ephemeral(ctx.guild_id)
            sql.Ephemeral.set_ephemeral(ctx.guild_id, False)
            await ctx.respond(content="設定しました。", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
        print(
            f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nsetting_channel - set")

def setup(bot):
    bot.add_cog(SettingCog(bot))
