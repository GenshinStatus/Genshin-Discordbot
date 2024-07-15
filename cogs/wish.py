from lib.yamlutil import yaml
import lib.sql as sql
import discord
from discord.ext import commands
from discord import Option, OptionChoice, SlashCommandGroup
from discord.ui import View
import random
import urllib
import asyncio

is_skip_button_pressed = False

MAJOR_VERSION_LIST = ["1","2","3","4"]
VERSION_RANGE_ENUM = {
    "0.0" : [200],
    "1.0" : [0],
    "1.1" : [1, 2],
    "1.2" : [3, 4],
    "1.3" : [5, 7],
    "1.4" : [8, 9],
    "1.5" : [10, 11],
    "1.6" : [12, 13],
    "2.0" : [14, 15],
    "2.1" : [16, 17],
    "2.2" : [18, 19],
    "2.3" : [20, 22],
    "2.4" : [23, 26],
    "2.5" : [27, 29],
    "2.6" : [30, 32],
    "2.7" : [33, 35],
    "2.8" : [36, 38],
    "3.0" : [39, 42],
    "3.1" : [43, 46],
    "3.2" : [47, 50],
    "3.3" : [51, 52],
    "3.4" : [53, 56],
    "3.5" : [57, 60],
    "3.6" : [61, 64],
    "3.7" : [65, 68],
    "3.8" : [69, 73],
    "4.0" : [73, 76],
    "4.1" : [77, 80],
    "4.2" : [81, 84],
    "4.3" : [85, 88],
    "4.4" : [89, 92],
    "4.5" : [93, 96],
    "4.6" : [97, 98],
    "4.7" : [99, 102],
    "4.8" : [103, 104],
}
MINOR_VERSION_RANGE_ENUM = {
    "0" : {
        "0.0" : [200]
    },
    "1" : {
        "1.0" : [0],
        "1.1" : [1, 2],
        "1.2" : [3, 4],
        "1.3" : [5, 7],
        "1.4" : [8, 9],
        "1.5" : [10, 11],
        "1.6" : [12, 13]
    },
    "2" : {
        "2.0" : [14, 15],
        "2.1" : [16, 17],
        "2.2" : [18, 19],
        "2.3" : [20, 22],
        "2.4" : [23, 26],
        "2.5" : [27, 29],
        "2.6" : [30, 32],
        "2.7" : [33, 35],
        "2.8" : [36, 38]
    },
    "3" : {
        "3.0" : [39, 42],
        "3.1" : [43, 46],
        "3.2" : [47, 50],
        "3.3" : [51, 52],
        "3.4" : [53, 56],
        "3.5" : [57, 60],
        "3.6" : [61, 64],
        "3.7" : [65, 68],
        "3.8" : [69, 73]
    },
    "4" : {
        "4.0" : [73, 76],
        "4.1" : [77, 80],
        "4.2" : [81, 84],
        "4.3" : [85, 88],
        "4.4" : [89, 92],
        "4.5" : [93, 96],
        "4.6" : [97, 98],
        "4.7" : [99, 102],
        "4.8" : [103, 104]
    }
}
# ファイル指定
genshinYaml = yaml('genshin.yaml')
genshinHYaml = yaml('genshinH.yaml')
bannerIDYaml = yaml('wish_bannerID.yaml')
wish_configYaml = yaml('wish_config.yaml')

# ファイル初期化
characterName = genshinYaml.load_yaml()
characterTrans = genshinHYaml.load_yaml()
banner_id = bannerIDYaml.load_yaml()
wish_config = wish_configYaml.load_yaml()


def genshingen(name):
    if name in characterName:
        if "url" in characterName[name]:
            return characterName[name]["url"]

        if "zh" in characterName[name]:
            result = characterName[name]["zh"]
        else:
            raise ValueError()
    elif name in characterTrans:
        result = characterName[characterTrans[name]["ja"]]["zh"]
    else:
        raise ValueError()

    result = urllib.parse.quote(result)

    return f"https://bbs.hoyolab.com/hoyowiki/picture/character/{result}/avatar.png"


changed_per = [20.627, 13.946, 9.429, 6.375, 4.306, 2.914,
               1.970, 1.332, 0.901, 0.608, 0.411, 0.278, 0.187, 0.126, 0.265]

def getPer(roof: int):
    '''
    現在の天井から確率を出してくれるいい奴
    '''
    one_roof = roof % 90
    if one_roof == 0:
        hoge = changed_per[-1]
    elif one_roof <= 75:
        hoge = 0.603-0.003*one_roof
    else:
        try:
            hoge = changed_per[roof-76]
        except:
            hoge = changed_per[roof-166]
    return hoge/100


def roofReset(id: int, roof: int):
    '''
    指定した天井の数値にするよ
    '''
    hoge = sql.WishUser.get_wish_user(id=id)
    sql.WishUser.update_wish_user(
        id=id, char_roof=roof, weap_roof=hoge.weapon_loof, custom_id=hoge.wishnum)
    return


def roofGet(id: int, roof: int):
    '''
    idから天井を足して結果をintで返すよ
    '''
    hoge = sql.WishUser.get_wish_user(id=id)
    roof += hoge.char_loof
    sql.WishUser.update_wish_user(
        id=id, char_roof=roof, weap_roof=hoge.weapon_loof, custom_id=hoge.wishnum)
    return roof


def wish_list(roof: int, id: int):
    '''
    キャラを排出します
    '''
    # 天井から確率を計算
    per = getPer(roof)
    three = 1 - per - 0.051  # 星5が出ない確率 - 星4が出る確率
    five = per / 2  # すり抜け分です

    if roof == 180:
        # 二度目の天井。確定で6を追加。ついでに天井リセット。
        tmpresalt = ["6"]
        roofReset(id, 0)

    elif roof == 90:
        # 一度目の天井に達した確率。2/1の確率で5か6を追加。
        tmpresalt = random.choices(["5", "6"], weights=[0.5, 0.5])
        if "6" in tmpresalt:  # 6が出た場合は天井リセットです。
            roofReset(id, 0)
        return "".join(tmpresalt)

    elif roof % 10 > 0:
        # 通常の確率。
        tmpresalt = random.choices(["3", "4", "5", "6"], weights=[
                                   three, 0.051, five, five])
        if "5" in tmpresalt:  # 星5が出た場合は、星5が出なくなる天井カウント90に、
            roofReset(id, 90)
        elif "6" in tmpresalt:  # 星6が出た場合は天井カウントをリセットします。
            roofReset(id, 0)

    elif roof % 10 == 0:
        # 星4天井システム。必ず星4以上を追加します。
        tmpresalt = random.choices(["3", "4", "5", "6"], weights=[
            three, 0.051, five, five])
        if "5" in tmpresalt:  # 星5が出た場合は、星5が出なくなる天井カウント90に、
            roofReset(id, 90)
        elif "6" in tmpresalt:  # 星6が出た場合は天井カウントをリセットします。
            roofReset(id, 0)
        else:
            tmpresalt = ["4"]

    if roof > 90:
        # 一度目の天井以降の確率。5は出ない。
        if "5" in tmpresalt:  # 5の場合6にし、天井と確率リセット。
            tmpresalt = ["6"]
            roofReset(id, 0)

    return "".join(tmpresalt)


class Wish_bataCog(commands.Cog):

    def __init__(self, bot):
        print('wish初期化.')
        self.bot = bot

    def embeded(title, description, url):
        embed = discord.Embed(title=title, color=0x1e90ff,
                              description=description)
        embed.set_image(url=url)
        return embed

    wish = SlashCommandGroup('wish', 'test')

    @wish.command(name="get", description="原神ガチャシミュレーター")
    async def get(
            self,
            ctx: discord.ApplicationContext):

        await ctx.respond(content="祈願バナーを選択してください。", view=SelectModeBannerButton(resolution="low"), ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))

    @wish.command(name="get_original", description="原神ガチャシミュレーター・オリジナル（アーロイガチャなど）")
    async def get_original(
            self,
            ctx: discord.ApplicationContext):

        await ctx.respond(content="祈願バナーを選択してください。", view=wish_original_banner_select_View(resolution="low"), ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))

    @wish.command(name="get_image", description="ガチャイラスト取得")
    async def character(
        self,
        ctx: discord.ApplicationContext,
        content: Option(str, required=True, description="キャラ名 (ひらかなでもOK)")
    ):
        try:
            picture = genshingen(content)
        except:
            content = f" \"{content}\" は原神データベースに存在しません。"
            embed = discord.Embed(title=content, color=0x1e90ff,)
            await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
            return
        embed = discord.Embed(title=content, color=0x1e90ff,)
        embed.set_image(url=picture)
        await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))


class wish_main_system_value():
    def __init__(self, id, banner_id, roof, resalt, final_resalt, resolution):
        self.id = id
        self.banner_id = banner_id
        self.roof = roof
        self.resalt = resalt
        self.final_resalt = final_resalt
        self.resolution = resolution


def get_wish_display_embed(DATA: wish_main_system_value, v):
    if "3" == DATA.resalt[v]:
        color = 0x1e90ff
    elif "4" == DATA.resalt[v]:
        color = 0x8a2be2
    elif "5" or "6" == DATA.resalt[v]:
        color = 0xff8c00
    embed = discord.Embed(title=f"{DATA.final_resalt[v]} ({v}/{len(DATA.final_resalt)})", color=color)
    print(f"https://genshin-cdn.cinnamon.works/wish/screen/{DATA.resolution}/"+urllib.parse.quote(DATA.final_resalt[v])+".jpg")
    embed.set_image(url=f"https://genshin-cdn.cinnamon.works/wish/screen/{DATA.resolution}/"+urllib.parse.quote(DATA.final_resalt[v])+".jpg")
    return embed


def get_wish_resalt_display_embed(DATA: wish_main_system_value):
    bannerIDYaml = yaml('wish_bannerID.yaml')
    banner_DATA = bannerIDYaml.load_yaml()
    banner_id = int(DATA.banner_id)
    roof = int(DATA.roof)
    embed = discord.Embed(
        title="ガチャ結果",
        description=f"""
        祈願バナー: **{banner_DATA[banner_id]['name']}・{''.join(banner_DATA[banner_id]['pickup_5'])} ({banner_DATA[banner_id]['ver']})**
        引いた人: <@{DATA.id}>
        現在のあなたの天井値: **{roof-1}**
        最終祈願の疑似星5確率: **{round(getPer(roof)*100, 2)}%**
        PU天井からの原石消費数: **{roof * 160}個**
        1原石2円としたときの消費金額: **{roof * 320}円**
        """,
        color=0x1e90ff)

    hoge = -1
    resalt_list = []
    for n in DATA.final_resalt:
        hoge += 1
        ster = DATA.resalt[hoge]
        if ster == "6":
            ster = "5"
        if ster == "5":
            resalt_list.append(f"**★★★★★ {DATA.final_resalt[hoge]}**")
            continue
        elif ster == "4":
            resalt_list.append(f"**★{ster} {DATA.final_resalt[hoge]}**")
            continue
        resalt_list.append(f"☆{ster} {DATA.final_resalt[hoge]}")

    embed.add_field(
        name=f"ガチャ結果（祈願回数: {len(DATA.resalt)}）", value="\n".join(resalt_list))
    return embed


def get_banner_embed(banner__id: int):
    banner_data = banner_id[banner__id]
    embed = discord.Embed(title=f"{banner_data['name']}",
                          description=f"{banner_data['ver']} {''.join(banner_data['pickup_5'])}",
                          color=0x1e90ff,)
    embed.set_image(
        url=f"https://genshin-cdn.cinnamon.works/wish/banner/character/{banner__id}.jpg")
    return embed

def version_to_banner_id(version: str):
        wish_select_options: list[discord.SelectOption] = []
        if VERSION_RANGE_ENUM[version][0] == 0:
            wish_select_options.append(
                discord.SelectOption(label=f'{banner_id[0]["ver"]} {"".join(banner_id[0]["pickup_5"])}', description=", ".join(banner_id[0]["pickup_4"]), value=str(0)))
        elif VERSION_RANGE_ENUM[version][0] == 200:
            wish_select_options.append(
                discord.SelectOption(label=f'{banner_id[200]["ver"]} {"".join(banner_id[200]["pickup_5"])}', description=", ".join(banner_id[200]["pickup_4"]), value=str(200)))
        else:
            for n in range(VERSION_RANGE_ENUM[version][0], VERSION_RANGE_ENUM[version][1]+1):
                wish_select_options.append(
                    discord.SelectOption(label=f'{banner_id[n]["ver"]} {"".join(banner_id[n]["pickup_5"])}', description=", ".join(banner_id[n]["pickup_4"]), value=str(n)))
        return wish_select_options

def major_version_to_minor_version(major_version: str):
    minor_select_options: list[discord.SelectOption] = []
    for n in MINOR_VERSION_RANGE_ENUM[major_version].keys():
        minor_select_options.append(discord.SelectOption(label=n, value=n))
    return minor_select_options

class wish_original_banner_select_View(View):
    def __init__(self, resolution):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.resolution = resolution
    
    @discord.ui.select(
        placeholder="ガチャを指定（オリジナル祈願）",
        options=version_to_banner_id("0.0")
    )
    async def select_callback_0(self, select: discord.ui.Select, interaction: discord.Interaction):
        view = wish_select_View(banner_id=int(select.values[0]), resolution=self.resolution)
        print(
            f"実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nオリジナル")
        await interaction.response.edit_message(content=f"祈願回数を指定してください。", embed=get_banner_embed(int(select.values[0])), view=view)


# バージョンを受け取り、MINOR_VERSION_RANGE_ENUMにある範囲のbanner_idを取得し、セレクトメニューを表示する
class BannerSelect(discord.ui.Select):
    def __init__(self, version: str, resolution: str):
        super().__init__(
            placeholder="ガチャを指定",
            options=version_to_banner_id(version)
        )
        self.resolution = resolution

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=f"祈願回数を指定してください。", embed=get_banner_embed(int(self.values[0])), view=wish_select_View(banner_id=int(self.values[0]), resolution=self.resolution))

# MINOR_VERSION_RANGE_ENUMの最後のバージョンを取得し、BannerSelectクラスに渡す
class SelectModeBannerButton(View):
    def __init__(self, resolution: str = "low"):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.resolution = resolution

    @discord.ui.button(label="最新バージョンから選択する", style=discord.ButtonStyle.green)
    async def callback1(self, _: discord.ui.Button, interaction: discord.Interaction):
        view = View()
        view.add_item(BannerSelect(version="".join([i for i in VERSION_RANGE_ENUM.keys()][-1]), resolution=self.resolution))
        view.add_item(ReSelectButton(resolution=self.resolution))
        await interaction.response.edit_message(content="祈願バナーを選択してください。", embed=None, view=view)

    @discord.ui.button(label="過去のバージョンから選択する", style=discord.ButtonStyle.green)
    async def callback2(self, _: discord.ui.Button, interaction: discord.Interaction):
        view = View()
        view.add_item(MajorVersionSelect(resolution=self.resolution))
        view.add_item(ReSelectButton(resolution=self.resolution))
        await interaction.response.edit_message(content="バージョンを選択してください。", embed=None, view=view)

# メジャーバージョンを受け取り、マイナーバージョンを選択するセレクトメニューを表示する
class MinorVersionSelect(discord.ui.Select):
    def __init__(self, version: str, resolution: str):
        super().__init__(
            placeholder="バージョンを指定",
            options=major_version_to_minor_version(version)
        )
        self.resolution = resolution

    async def callback(self, interaction: discord.Interaction):
        view = View()
        view.add_item(BannerSelect(version=self.values[0], resolution=self.resolution))
        view.add_item(ReSelectButton(resolution=self.resolution))
        await interaction.response.edit_message(content="バージョンを選択してください。", embed=None, view=view)

# メジャーバージョンを選択するセレクトメニューを表示する
class MajorVersionSelect(discord.ui.Select):
    def __init__(self, resolution: str):
        super().__init__(
            placeholder="バージョンを指定",
            options=[discord.SelectOption(label=f"{i}.0", value=i) for i in MAJOR_VERSION_LIST]
        )
        self.resolution = resolution

    async def callback(self, interaction: discord.Interaction):
        view = View()
        view.add_item(MinorVersionSelect(version=self.values[0], resolution=self.resolution))
        view.add_item(ReSelectButton(resolution=self.resolution))
        await interaction.response.edit_message(content="バージョンを選択してください。", embed=None, view=view)

class wish_select_View(View):
    def __init__(self, banner_id: int, resolution):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.banner_id = banner_id
        self.resolution = resolution

    @discord.ui.button(label="1回")
    async def once(self, _: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="ローディング", view=None)
        await get_wish_resalt(interaction, 1, self.banner_id, self.resolution)

    @discord.ui.button(label="10回")
    async def twice(self, _: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="ローディング", view=None)
        await get_wish_resalt(interaction, 10, self.banner_id, self.resolution)

    @discord.ui.button(label="回数指定")
    async def enter(self, _: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(modal=select_wish_modal(interaction, self.banner_id, self.resolution))


class select_wish_modal(discord.ui.Modal):
    def __init__(self, interaction, banner_id, resolution):
        super().__init__(title="祈願回数を入力してください。", timeout=300,)
        self.interaction = interaction
        self.banner_id = banner_id
        self.resolution = resolution

        self.num = discord.ui.InputText(
            label="祈願回数を半角数字で入力してください。（100連まで）",
            style=discord.InputTextStyle.short,
            value="90",
            placeholder="90",
        )
        self.add_item(self.num)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="ローディング", view=None)
        try:
            hoge = int(self.num.value)
            if hoge > 100:
                raise
            await get_wish_resalt(self.interaction, hoge, self.banner_id, resolution=self.resolution)
        except:
            await interaction.edit_original_response(content="入力された数値が無効です。", view=None)


async def get_wish_resalt(interaction: discord.Interaction, num, banner_id, resolution):
    id = interaction.user.id
    # まずこいつの天井、指定バナーを取得
    roof = roofGet(id, 0)

    # とりあえず天井から結果num回を排出
    await interaction.edit_original_response(content="ガチャ結果読み込み中...")
    resalt = []
    for n in range(num):
        resalt.append(wish_list(roof=roof, id=id))
        roof = roofGet(id, 1)
    # random.shuffle(resalt)

    # 結果からキャラ名に変換
    await interaction.edit_original_response(content="ガチャ画面読み込み中...")
    final_resalt = []
    for ster in resalt:
        final_resalt.append(number_to_character(ster, banner_id))

    # 全部の変数まとめ
    DATA = wish_main_system_value(
        id=id, banner_id=banner_id, roof=roof, resalt=resalt, final_resalt=final_resalt, resolution=resolution)

    await interaction.edit_original_response(content="演出画面読み込み中...")
    global is_skip_button_pressed
    is_skip_button_pressed = False
    # 条件分岐で画像変化
    view = View()
    view.add_item(WishSkipButton(interaction, DATA))
    if "5" in resalt or "6" in resalt:
        direction_embed = Wish_bataCog.embeded(
            None, None, "https://c.tenor.com/rOuL0G1uRpMAAAAC/genshin-impact-pull.gif")
        await interaction.edit_original_response(content=None, embed=direction_embed, view=view)
    else:
        direction_embed = Wish_bataCog.embeded(
            None, None, "https://c.tenor.com/pVzBgcp1RPQAAAAC/genshin-impact-animation.gif")
        await interaction.edit_original_response(content=None, embed=direction_embed, view=view)
    await asyncio.sleep(5.5)

    if is_skip_button_pressed == False:
        view = View()
        view.add_item(GotoNextButton(interaction, DATA, 0))
        view.add_item(GotoResultButton(interaction, DATA))
        view.add_item(Wish_image_change_Button(interaction, DATA, 0))
        await interaction.edit_original_response(content=None, embed=get_wish_display_embed(DATA, 0), view=view)


def number_to_character(num, banner__id: int):
    banner_data = banner_id[banner__id]
    if num == "3":
        return "".join(random.choices(wish_config["weapon_3"]))
    if num == "4":
        sterresalt = random.choices(
            ["char_4", "weapon_4", "pickup_4"], weights=[0.25, 0.25, 0.5])
        if sterresalt != ["pickup_4"]:
            return "".join(random.choices(wish_config["".join(sterresalt)]))
        else:
            return "".join(random.choices(banner_data["pickup_4"]))
    if num == ["5"] or num == "5":
        return "".join(random.choices(wish_config["char_5"]))
    if num == ["6"] or num == "6":
        return "".join(banner_data["pickup_5"])


# スキップボタンを表示させるボタン


class WishSkipButton(discord.ui.Button):
    def __init__(self, interaction, DATA: wish_main_system_value):
        super().__init__(label="スキップ", style=discord.ButtonStyle.green)
        self.interaction = interaction
        self.DATA = DATA

    async def callback(self, interaction: discord.Interaction):
        global is_skip_button_pressed
        is_skip_button_pressed = True
        view = View()
        view.add_item(GotoNextButton(self.interaction, self.DATA, 0))
        view.add_item(GotoResultButton(self.interaction, self.DATA))
        view.add_item(Wish_image_change_Button(interaction, self.DATA, 0))
        await interaction.response.edit_message(content=None, embed=get_wish_display_embed(self.DATA, 0), view=view)

# 次のボタンを表示させるボタン


class GotoNextButton(discord.ui.Button):
    def __init__(self, interaction, DATA: wish_main_system_value, v):
        super().__init__(label="続ける", style=discord.ButtonStyle.green)
        self.interaction = interaction
        self.DATA = DATA
        self.v = v

    async def callback(self, interaction: discord.Interaction):
        if self.v < len(self.DATA.final_resalt)-1:
            self.v += 1
            view = View()
            view.add_item(GotoNextButton(
                self.interaction, self.DATA, self.v))
            view.add_item(GotoResultButton(
                self.interaction, self.DATA))
            view.add_item(Wish_image_change_Button(interaction, self.DATA, self.v))
            await interaction.response.edit_message(content=None, embed=get_wish_display_embed(self.DATA, self.v), view=view)
        else:
            await interaction.response.edit_message(content="読み込み中...", embed=None, view=None)
            view = View()
            view.add_item(Wish_again_Button(
                self.interaction, self.DATA))
            view.add_item(Wish_resetting_Button(self.interaction, self.DATA))
            await interaction.edit_original_response(content=None, embed=get_wish_resalt_display_embed(self.DATA), view=view)

# 全部飛ばすボタン


class GotoResultButton(discord.ui.Button):
    def __init__(self, interaction, DATA: wish_main_system_value):
        super().__init__(label="結果を見る", style=discord.ButtonStyle.green)
        self.interaction = interaction
        self.DATA = DATA

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="読み込み中...", embed=None, view=None)
        view = View()
        view.add_item(Wish_again_Button(
            self.interaction, self.DATA))
        view.add_item(Wish_resetting_Button(self.interaction, self.DATA))
        await interaction.edit_original_response(content=None, embed=get_wish_resalt_display_embed(self.DATA), view=view)

# もう一回遊べるどん


class Wish_again_Button(discord.ui.Button):
    def __init__(self, interaction, DATA: wish_main_system_value):
        super().__init__(label="もう一度祈願する", style=discord.ButtonStyle.green)
        self.interaction = interaction
        self.DATA = DATA

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="ローディング", view=None)
        await get_wish_resalt(interaction, len(self.DATA.resalt), self.DATA.banner_id, self.DATA.resolution)

# 設定変えたい人用


class Wish_resetting_Button(discord.ui.Button):
    def __init__(self, interaction, DATA: wish_main_system_value):
        super().__init__(label="違うガチャを引く", style=discord.ButtonStyle.gray)
        self.interaction = interaction
        self.DATA = DATA

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="祈願バナーを選択してください。", embed=None, view=SelectModeBannerButton(resolution=self.DATA.resolution))

class ReSelectButton(discord.ui.Button):
    def __init__(self, resolution):
        super().__init__(label="選びなおす", style=discord.ButtonStyle.gray)
        self.resolution = resolution

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="祈願バナーを選択してください。", embed=None, view=SelectModeBannerButton(resolution=self.resolution))

# 表示される画像を低画質と高画質で切り替えるボタン。フリップフロップのように切り替える。ラベルも切り替える。

class Wish_image_change_Button(discord.ui.Button):
    def __init__(self, interaction, DATA: wish_main_system_value, v):
        print(DATA.resolution)
        if DATA.resolution == "low":
            super().__init__(label="高画質に切り替える", style=discord.ButtonStyle.gray)
        else:
            super().__init__(label="低画質に切り替える", style=discord.ButtonStyle.gray)
        self.interaction = interaction
        self.DATA = DATA
        self.v = v

    async def callback(self, interaction: discord.Interaction):
        if self.DATA.resolution == "low":
            self.DATA.resolution = "high"
        else:
            self.DATA.resolution = "low"
        view = View()
        view.add_item(GotoNextButton(
            self.interaction, self.DATA, self.v))
        view.add_item(GotoResultButton(
            self.interaction, self.DATA))
        view.add_item(Wish_image_change_Button(
            self.interaction, self.DATA, self.v))

        await interaction.response.edit_message(content=None, embed=get_wish_display_embed(self.DATA, self.v), view=view)

def setup(bot):
    bot.add_cog(Wish_bataCog(bot))
