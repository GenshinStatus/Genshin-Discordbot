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

charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinJp = genshinJpYaml.load_yaml()
l: list[discord.SelectOption] = []


class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, label: str, uid: str, dict, data):
        super().__init__(style=discord.ButtonStyle.secondary, label=label)
        self.dict = dict
        self.uid = uid
        self.data = data

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        print(self.uid)

        await interaction.response.edit_message(content="```読み込み中...（10秒ほどかかります）```", embed=None, view=None)
        self.style = discord.ButtonStyle.success
        # ラベル（名前）からIDを割り出す
        # 多分「名前：iD」ってなってるはず
        id = self.dict[self.label]
        log_output_interaction(interaction=interaction,
                               cmd=f"genshinstat get キャラ取得 {self.uid}")
        for child in self.view.children:
            child.style = discord.ButtonStyle.gray
        # await interaction.response.edit_message(content=content, embed=await getStat.get(self.uid, id), view=TicTacToe(self.data,self.uid))
        try:
            # キャラクターのデータを取得します。
            json = await CharacterStatus.get_json(uid=self.uid)
            character_status = CharacterStatus.getCharacterStatus(
                json=json, id=id, build_type=self.view.build_type)

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
            view=TicTacToe(self.data, self.uid)
        )


class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]

    def __init__(self, data, uid, build_type: str):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.build_type = build_type
        names = []
        dict = {}
        # 入ってきたidを名前にしてリスト化
        for id in data:
            id = str(id)
            name = genshinJp[characters[str(id)]["NameId"]]
            names.append(name)
            dict.update({name: id})
        # 名前をラベル、ついでにdictとuidも送り付ける
        for v in names:
            self.add_item(TicTacToeButton(v, uid, dict, data))

# モーダルを表示させるボタン


class UidModalButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="登録せずにUIDから検索", style=discord.ButtonStyle.green)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UidModal(self.ctx))

# UIDを聞くモーダル


class UidModal(discord.ui.Modal):
    def __init__(self, ctx):
        super().__init__(title="UIDを入力してください。", timeout=300,)
        self.ctx = ctx

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
        uid = self.uid.value
        ctx = self.ctx
        await uid_respond(self, interaction, ctx, uid, self.view.build_type)

# UIDを表示させるボタン


class UidButton(discord.ui.Button):
    def __init__(self, ctx, uid):
        super().__init__(label="登録されたUIDを使う", style=discord.ButtonStyle.green)
        self.ctx = ctx
        self.uid = uid

    async def callback(self, interaction: discord.Interaction):
        ctx = self.ctx
        uid = self.uid
        build_type = self.view.build_type
        await uid_respond(self, interaction, ctx, uid, build_type)


async def uid_respond(self, interaction: discord.Interaction, ctx, uid, build_type: str):
    await interaction.response.edit_message(content="アカウント情報読み込み中...", view=None)
    try:
        url = f"https://enka.network/api/uid/{uid}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.json()
                resalt = []
    except:
        await interaction.edit_original_message(content="エラー：入力されたものが存在するUIDではありません")
        return

    if resp == {}:
        await interaction.edit_original_message(content="エラー：現在、EnkaNetworkはメンテナンス中です。復旧までしばらくお待ちください。")
        return

    await interaction.edit_original_message(content="キャラ情報読み込み中...")
    embed = await GenshinCog.getApi(self, uid, resp)
    await interaction.edit_original_message(content="画像を生成中...")
    try:
        file = await getPicture.getProfile(uid, resp)
        hoge = discord.File(file, f"{uid}.png")
        for id in resp["playerInfo"]["showAvatarInfoList"]:
            resalt.append(id["avatarId"])
        await interaction.edit_original_message(content="ボタンを生成中...")
        await interaction.edit_original_message(content=None, embed=embed, view=TicTacToe(resalt, uid, build_type), file=hoge)
    except:
        embed.add_field(name="エラー", value="キャラ情報を一切取得できませんでした。原神の設定を確認してください。")
        await interaction.edit_original_message(content=None, embed=embed, file=hoge)
    finally:
        del hoge
        os.remove(file)


class select_uid_pulldown(discord.ui.Select):
    def __init__(self, ctx, selectOptions: list[discord.SelectOption], game_name):
        super().__init__(placeholder="表示するUIDを選択してください", options=selectOptions)
        self.ctx = ctx
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        await uid_respond(self, interaction, self.ctx, self.values[0], self.view.build_type)


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

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.build_type = self.values[0]

        await interaction.response.edit_message(view=view)


class GenshinCog(commands.Cog):

    def __init__(self, bot):
        print('genshin初期化')
        self.bot = bot

    async def getApi(self, uid, resp):
        try:
            embed = discord.Embed(
                title=f"{resp['playerInfo']['nickname']}",
                color=0x1e90ff,
                description=f"uid: {uid}",
                url=f"https://enka.network/api/uid/{uid}"
            )
            embed.set_image(url=f"attachment://{uid}.png")
            return embed
        except:
            embed = discord.Embed(
                title=f"エラーが発生しました。APIを確認してからもう一度お試しください。\n{f'https://enka.network/api/uid/{uid}'}",
                color=0x1e90ff,
                url=f"https://enka.network/api/uid/{uid}"
            )
            return embed

    genshin = SlashCommandGroup('genshinstat', 'test')

    @genshin.command(name="get", description="UIDからキャラ情報を取得し、画像を生成します")
    async def genshin_get(
            self,
            ctx: discord.ApplicationContext,
    ):
        view = View(timeout=300, disable_on_timeout=True)
        select_options: list[discord.SelectOption] = []
        userData = SQL.User.get_user_list(ctx.author.id)

        view = View(timeout=300, disable_on_timeout=True)

        view.build_type = SubTypes.ATTACK_PERCENT.value
        view.add_item(BuildTypeSelecter())
        #  登録してないときの処理
        if userData == []:
            view.add_item(uidlist.UidModalButton(ctx))
            view.add_item(UidModalButton(ctx))
            await ctx.respond(content="UIDが登録されていません。下のボタンから登録すると、UIDをいちいち入力する必要がないので便利です。\n下のボタンから、登録せずに確認できます。", view=view, ephemeral=True)
            return

        #  1つだけ登録してたときの処理
        if len(userData) == 1:
            view.add_item(UidButton(ctx, userData[0].uid))
            view.add_item(UidModalButton(ctx))
            await ctx.respond(content="UIDが登録されています。登録されているUIDを使うか、直接UIDを指定するか選んでください。", view=view, ephemeral=True)
            return

        #  それ以外
        for v in userData:
            select_options.append(
                discord.SelectOption(label=v.game_name, description=str(v.uid), value=str(v.uid)))
        view.add_item(select_uid_pulldown(ctx, select_options, v.game_name))
        view.add_item(UidModalButton(ctx))
        await ctx.respond(content="UIDが複数登録されています。表示するUIDを選ぶか、ボタンから指定してください。", view=view, ephemeral=True)
        return


def setup(bot):
    bot.add_cog(GenshinCog(bot))
