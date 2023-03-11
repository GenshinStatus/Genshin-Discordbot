import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks
from discord import Option, SlashCommandGroup
import aiohttp
from lib.yamlutil import yaml
import lib.picture as getPicture
from typing import List
import lib.sql as SQL
import cogs.uidlist as uidlist
import os
from lib.getCharacterStatus import CharacterStatus
from enums.substatus import SubTypes
from enums.ImageTypeEnums import ImageTypeEnums
from lib.gen_genshin_image import get_character_discord_file
from lib.log_output import log_output, log_output_interaction
from model.genshin_model import GenshinUID
import view.genshin_view as genshin_view


async def get_profile(uid, interaction: discord.Interaction):
    await interaction.response.edit_message(content='プロフィールをロード中...', view=None)
    status = GenshinUID(str(uid))
    status.data = await status.get_data()
    status.character_list = status.get_character_list()
    file = await status.get_profile_discord_file()
    embed = status.get_profile_embed()
    view = View(timeout=300, disable_on_timeout=True)
    # view.add_item(genshin_view.ScoreTypeSelecter(status))
    # view.add_item(genshin_view.ImageTypeSelecter(status))
    view = status.get_character_button(view=view)
    await interaction.edit_original_message(content=None, embed=embed, file=file, view=view)


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
        await get_profile(self.uid.value, interaction)


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
        await get_profile(self.uid, interaction)


class select_uid_pulldown(discord.ui.Select):
    def __init__(self, selectOptions: list[discord.SelectOption], game_name):
        super().__init__(placeholder="表示するUIDを選択してください", options=selectOptions)
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        await get_profile(self.values[0], interaction)


class GenshinCog(commands.Cog):

    def __init__(self, bot):
        print('genshin初期化')
        self.bot = bot

    genshin = SlashCommandGroup('genshinstat', 'test')

    @genshin.command(name="get", description="UIDからキャラ情報を取得し、画像を生成します")
    async def genshin_get(
            self,
            ctx: discord.ApplicationContext,
    ):
        view = View(timeout=300, disable_on_timeout=True)
        select_options: list[discord.SelectOption] = []
        userData = SQL.User.get_user_list(ctx.author.id)

        #  登録してないときの処理
        if userData == []:
            view.add_item(uidlist.UidModalButton())
            view.add_item(UidModalButton())
            await ctx.respond(content="UIDが登録されていません。下のボタンから登録すると、UIDをいちいち入力する必要がないので便利です。\n下のボタンから、登録せずに確認できます。",
                              view=view,
                              ephemeral=True)
            return

        #  1つだけ登録してたときの処理
        if len(userData) == 1:
            view.add_item(UidButton(userData[0].uid))
            view.add_item(UidModalButton())
            await ctx.respond(content="UIDが登録されています。登録されているUIDを使うか、直接UIDを指定するか選んでください。", view=view, ephemeral=True)
            return

        #  それ以外
        for v in userData:
            select_options.append(
                discord.SelectOption(label=v.game_name, description=str(v.uid), value=str(v.uid)))
        view.add_item(select_uid_pulldown(select_options, v.game_name))
        view.add_item(UidModalButton())
        await ctx.respond(content="UIDが複数登録されています。表示するUIDを選ぶか、ボタンから指定してください。", view=view, ephemeral=True)
        return


def setup(bot):
    bot.add_cog(GenshinCog(bot))
