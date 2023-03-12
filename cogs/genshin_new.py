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
from lib.gen_genshin_image import get_character_discord_file
from lib.log_output import log_output, log_output_interaction

charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinJp = genshinJpYaml.load_yaml()


async def get_character_json(uid):
    url = f"https://enka.network/api/uid/{uid}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            resp = await response.json()
    return resp


class BuildTypeSelecter(discord.ui.Select):
    def __init__(self) -> None:
        super().__init__(placeholder="ビルドタイプを選択してください。")

        self.add_option(label=SubTypes.ATTACK_PERCENT.value,
                        value=SubTypes.ATTACK_PERCENT.value)
        self.add_option(label=SubTypes.CHARGE_EFFICIENCY.value,
                        value=SubTypes.CHARGE_EFFICIENCY.value)
        self.add_option(label=SubTypes.DEFENSE_PERCENT.value,
                        value=SubTypes.DEFENSE_PERCENT.value)
        self.add_option(label=SubTypes.HP_PERCENT.value,
                        value=SubTypes.HP_PERCENT.value)
        self.add_option(label=SubTypes.ELEMENT_MASTERY.value,
                        value=SubTypes.ELEMENT_MASTERY.value)


class CharacterSelectButton(discord.ui.Button):
    def __init__(self, label, status_data, dict):
        super().__init__(style=discord.ButtonStyle.gray, label=label)
        self.dict = dict
        self.uid = status_data.uid
        self.data = status_data.data
        self.build_type = status_data.build_type
        self.status_data = status_data

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        print(self.uid)

        await interaction.response.edit_message(content="```読み込み中...（10秒ほどかかります）```", embed=None, view=None)
        self.style = discord.ButtonStyle.success
        # ラベル（名前）からIDを割り出す
        # 多分「名前：iD」ってなってるはず
        self.status_data.set_character_id(
            self.status_data, self.dict[self.label])
        log_output_interaction(interaction=interaction,
                               cmd=f"genshinstat get キャラ取得 {self.uid}")
        try:
            # キャラクターのデータを取得します。
            json = await CharacterStatus.get_json(uid=self.uid)
            character_status = CharacterStatus.getCharacterStatus(
                json=json, id=id, build_type=self.build_type)

            # 画像データを取得し、DiscordのFileオブジェクトとしてurlとfileを取得します。
            file, url = get_character_discord_file(
                character_status=character_status
            )
        except ArithmeticError as e:
            # 失敗したときの処理かく
            # 例外によって種類わける
            pass

        # 取得した画像でembed作成しれすぽんす
        embed = discord.Embed(
            title=f"{self.label}",
            color=0x1e90ff,
        )

        embed.set_image(url=url)
        await interaction.edit_original_message(
            content=None,
            embed=embed,
            file=file,
            view=self.status_data.viewD)


class GenshinStatusClass():
    def __init__(self) -> None:
        self.uid = None
        self.data = None
        self.character_list = []
        self.character_id = None
        self.score_type = SubTypes.ATTACK_PERCENT.value
        self.view = View(timeout=300, disable_on_timeout=True)

    def set_character_id(self, id):
        self.character_id = id
        return self

    async def set_uid(self, status_data, uid):
        status_data.uid = uid
        status_data.data = await self.get_data(status_data)
        status_data.character_list = self.get_character_list(status_data)
        return status_data

    async def get_data(self, status_data):
        data = await get_character_json(status_data.uid)
        return data

    def get_character_list(self, status_data):
        character_list = []
        for id in status_data.data["playerInfo"]["showAvatarInfoList"]:
            character_list.append(id["avatarId"])
        return character_list

    def get_embed_profile(self, status_data):
        try:
            embed = discord.Embed(
                title=f"{status_data.data['playerInfo']['nickname']}",
                color=0x1e90ff,
                description=f"uid: {status_data.uid}",
                url=f"https://enka.network/api/uid/{status_data.uid}"
            )
            embed.set_image(url=f"attachment://{status_data.uid}.png")
            return embed
        except:
            embed = discord.Embed(
                title=f"エラーが発生しました。APIを確認してからもう一度お試しください。\n{f'https://enka.network/api/uid/{status_data.uid}'}",
                color=0x1e90ff,
                url=f"https://enka.network/api/uid/{status_data.uid}"
            )
            return embed

    async def generate_profile(self, status_data, interaction):
        file = await getPicture.getProfile(status_data.uid, status_data.data)
        hoge = discord.File(file, f"{status_data.uid}.png")
        await interaction.edit_original_message(
            content=None,
            embed=self.get_embed_profile(),
            view=self.view_add_button(status_data),
            file=hoge)

    def view_add_button(self, status_data):
        names = []
        dict = {}
        # 入ってきたidを名前にしてリスト化
        for id in status_data.character_list:
            id = str(id)
            name = genshinJp[characters[str(id)]["NameId"]]
            names.append(name)
            dict.update({name: id})
        # 名前をラベル、ついでにdictとuidも送り付ける
        for v in names:
            status_data.view.add_item(
                CharacterSelectButton(v, status_data, dict))

    async def on_button_click(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.generate_image(self)
        await interaction.response.edit_message()

    async def on_select_menu_select(self, select_menu: BuildTypeSelecter, interaction: discord.Interaction):
        self.score_type = select_menu.values[0]
        self.generate_image(self)
        await interaction.response.edit_message()


class UidModal(discord.ui.Modal):  # UIDを聞くモーダル
    def __init__(self, status_data):
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
        self.status_data = status_data

    async def callback(self, interaction: discord.Interaction) -> None:
        self.status_data = await GenshinStatusClass.set_uid(
            status_data=self.status_data, uid=self.uid.value)
        await GenshinStatusClass.generate_profile(self.status_data, interaction)


class UidModalButton(discord.ui.Button):
    def __init__(self, status_data):
        super().__init__(label="登録せずにUIDから検索", style=discord.ButtonStyle.green)
        self.status_data = status_data

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UidModal(self.status_data))


class UidButton(discord.ui.Button):
    def __init__(self, status_data, uid):
        super().__init__(label="登録されたUIDを使う", style=discord.ButtonStyle.green)
        self.uid = uid
        self.status_data = status_data

    async def callback(self, interaction: discord.Interaction):
        self.status_data = await GenshinStatusClass.set_uid(
            status_data=self.status_data, uid=self.uid)
        await GenshinStatusClass.generate_profile(self.status_data, interaction)


class select_uid_pulldown(discord.ui.Select):
    def __init__(self, status_data, selectOptions: list[discord.SelectOption], game_name):
        super().__init__(placeholder="表示するUIDを選択してください", options=selectOptions)
        self.status_data = status_data
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        self.status_data = await GenshinStatusClass.set_uid(
            status_data=self.status_data, uid=self.values[0])
        await GenshinStatusClass.generate_profile(self, self.status_data, interaction)


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
        status_data = GenshinStatusClass()

        #  登録してないときの処理
        if userData == []:
            view.add_item(uidlist.UidModalButton(status_data))
            view.add_item(UidModalButton(status_data))
            await ctx.respond(content="UIDが登録されていません。下のボタンから登録すると、UIDをいちいち入力する必要がないので便利です。\n下のボタンから、登録せずに確認できます。",
                              view=view,
                              ephemeral=True)
            return

        #  1つだけ登録してたときの処理
        if len(userData) == 1:
            view.add_item(UidButton(status_data, userData[0].uid))
            view.add_item(UidModalButton(status_data))
            await ctx.respond(content="UIDが登録されています。登録されているUIDを使うか、直接UIDを指定するか選んでください。", view=view, ephemeral=True)
            return

        #  それ以外
        for v in userData:
            select_options.append(
                discord.SelectOption(label=v.game_name, description=str(v.uid), value=str(v.uid)))
        view.add_item(select_uid_pulldown(
            status_data, select_options, v.game_name))
        view.add_item(UidModalButton(status_data))
        await ctx.respond(content="UIDが複数登録されています。表示するUIDを選ぶか、ボタンから指定してください。", view=view, ephemeral=True)
        return


def setup(bot):
    bot.add_cog(GenshinCog(bot))
