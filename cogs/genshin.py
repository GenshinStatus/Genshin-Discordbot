import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks
from discord import Option, SlashCommandGroup
import lib.sql as SQL
import cogs.uidlist as uidlist
from lib.log_output import log_output, log_output_interaction
import view.genshin_view as genshin_view
from model.user_data_model import GenshinStatusModel

class UidModal(discord.ui.Modal):  # UIDを聞くモーダル
    def __init__(self):
        super().__init__(title="UIDを入力してください。", timeout=300,)

        self.uid = discord.ui.InputText(
            label="UID",
            style=discord.InputTextStyle.short,
            min_length=9,
            max_length=9,
            placeholder="000000000",
            required=True,
        )
        self.add_item(self.uid)

    async def callback(self, interaction: discord.Interaction) -> None:
        await genshin_view.get_profile(self.uid.value, interaction)


class UidModalButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="登録せずにUIDから検索", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UidModal())


class UidButton(discord.ui.Button):
    def __init__(self, uid):
        super().__init__(label="登録されたUIDを使う", style=discord.ButtonStyle.green)
        self.uid = uid

    async def callback(self, interaction: discord.Interaction):
        await genshin_view.get_profile(self.uid, interaction)


class select_uid_pulldown(discord.ui.Select):
    def __init__(self, selectOptions: list[discord.SelectOption], game_name):
        super().__init__(placeholder="表示するUIDを選択してください", options=selectOptions)
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        await genshin_view.get_profile(self.values[0], interaction)


class GenshinCog(commands.Cog):

    def __init__(self, bot):
        print('genshin初期化')
        self.bot = bot

    genshin = SlashCommandGroup('genshinstat', 'test')

    @commands.slash_command(name="status", description="UIDからキャラ情報を取得し、画像を生成します")
    async def status_command(
            self,
            ctx: discord.ApplicationContext
    ):
        await GenshinCog.input_uid(self, ctx)

    @genshin.command(name="get", description="UIDからキャラ情報を取得し、画像を生成します")
    async def genshin_get(
            self,
            ctx: discord.ApplicationContext,
    ):
        await GenshinCog.input_uid(self, ctx)

    async def input_uid(self, ctx):
        view = View(timeout=300, disable_on_timeout=True)
        select_options: list[discord.SelectOption] = []
        userData = SQL.User.get_user_list(ctx.author.id)

        #  登録してないときの処理
        if userData == []:
            view.add_item(uidlist.UidModalButton(ctx))
            view.add_item(UidModalButton())
            embed = genshin_view.MyEmbed(
                title='UID選択', description='UIDが登録されていません。下のボタンから登録すると、UIDをいちいち入力する必要がないので便利です。\n下のボタンから、登録せずに確認できます。')
            await ctx.respond(content=None,
                              embed=embed,
                              view=view, 
                              ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
            log_output(ctx=ctx, cmd="/genshinstat get 未登録")
            return

        #  1つだけ登録してたときの処理
        if len(userData) == 1:
            view.add_item(UidButton(userData[0].uid))
            view.add_item(UidModalButton())
            embed = genshin_view.MyEmbed(
                title='UID選択', description='UIDが登録されています。登録されているUIDを使うか、直接UIDを指定するか選んでください。')
            await ctx.respond(content=None, embed=embed, view=view, ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
            log_output(ctx=ctx, cmd="/genshinstat get 登録済")
            return

        #  それ以外
        for v in userData:
            select_options.append(
                discord.SelectOption(label=v.game_name, description=str(v.uid), value=str(v.uid)))
        view.add_item(select_uid_pulldown(select_options, v.game_name))
        view.add_item(UidModalButton())
        embed = genshin_view.MyEmbed(
            title='UID選択', description='UIDが複数登録されています。表示するUIDを選ぶか、ボタンから指定してください。')
        await ctx.respond(content=None, embed=embed, view=view, ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
        log_output(ctx=ctx, cmd="/genshinstat get 複数登録済")
        return


def setup(bot):
    bot.add_cog(GenshinCog(bot))
