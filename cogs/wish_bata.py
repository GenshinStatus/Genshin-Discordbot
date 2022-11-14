from webbrowser import get
from lib.yamlutil import yaml
import discord
from discord.ext import commands
from discord import Option, OptionChoice, SlashCommandGroup
from discord.ui import View
import random
import urllib
import asyncio
import lib.wish_image as wish_image

is_skip_button_pressed = False

# ファイル指定
wishYaml = yaml('wish.yaml')
genshinYaml = yaml('genshin.yaml')
genshinHYaml = yaml('genshinH.yaml')
genshinStarYaml = yaml('genshin_ster.yaml')
bannerIDYaml = yaml('wish_bannerID.yaml')
wish_configYaml = yaml('wish_config.yaml')
name_to_urlYaml = yaml('name_to_url.yaml')

# ファイル初期化
wishData = wishYaml.load_yaml()
characterName = genshinYaml.load_yaml()
characterTrans = genshinHYaml.load_yaml()
bannerData = genshinStarYaml.load_yaml()
banner_id = bannerIDYaml.load_yaml()
wish_config = wish_configYaml.load_yaml()
name_to_url = name_to_urlYaml.load_yaml()


def get_wish_select_options():
    # bot再起動しなくてもyaml更新できるようにするためにいちいち取得するようにする
    bannerIDYaml = yaml('wish_bannerID.yaml')
    banner_id = bannerIDYaml.load_yaml()

    wish_select_options_1: list[discord.SelectOption] = []
    wish_select_options_2: list[discord.SelectOption] = []
    wish_select_options_3: list[discord.SelectOption] = []

    for v, n in banner_id.items():
        if v <= 13:
            wish_select_options_1.append(
                discord.SelectOption(label=f'{n["ver"]} {"".join(n["pickup_5"])}', description=", ".join(n["pickup_4"]), value=str(v)))
        elif v <= 38:
            wish_select_options_2.append(
                discord.SelectOption(label=f'{n["ver"]} {"".join(n["pickup_5"])}', description=", ".join(n["pickup_4"]), value=str(v)))
        elif v <= 100:
            wish_select_options_3.append(
                discord.SelectOption(label=f'{n["ver"]} {"".join(n["pickup_5"])}', description=", ".join(n["pickup_4"]), value=str(v)))
    return wish_select_options_1, wish_select_options_2, wish_select_options_3, banner_id


def roofInit():
    wishYaml = yaml('wish.yaml')
    wishData = wishYaml.load_yaml()
    return wishData


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
    hoge = roofInit()
    hoge[id] = {"roof": roof, "banner": hoge[id]
                ["banner"], "num": hoge[id]["num"]}
    wishYaml.save_yaml(hoge)
    return


def roofGet(id: int, roof: int):
    '''
    idから天井を足して結果をintで返すよ
    '''
    hoge = roofInit()
    if id in hoge:
        roof += hoge[id]["roof"]
        banner = hoge[id]["banner"]
        num = hoge[id]["num"]
    else:
        roof = 0
        banner = 00000
        num = 0
    hoge[id] = {"roof": roof, "banner": banner, "num": num}
    wishYaml.save_yaml(hoge)
    return roof


def genshingen(name: str):
    '''
    名前（日本語名）からキャラの画像urlを返すよ
    '''
    if name in ["コレイ", "ティナリ", "旅人", "ニィロウ", "キャンディス", "セノ"]:
        return characterName[name]["url"]
    if name in characterName:
        resalt = urllib.parse.quote(characterName[name]["zh"])
    elif name in characterTrans:
        resalt = urllib.parse.quote(
            characterName[characterTrans[name]["ja"]]["zh"])
    else:
        resalt = None
    return f"https://bbs.hoyolab.com/hoyowiki/picture/character/{resalt}/avatar.png"


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


class probability_calculation():
    def __init__(self, ctx: discord.interactions.Interaction, banner_id: int, pickup_char_roof: int):
        self.ctx = ctx
        self.banner = banner_id
        self.roof = pickup_char_roof

    def banner_display_embed(self):
        """
        画像を表示するEmbedを返します。
        """
        embed = discord.Embed(
            title="ガチャ回数を指定してください。",
            color=0x1e90ff,
            description="バナーの切り替えなどは設定から行ってください。")
        image_id = None
        banner_name = None
        embed.add_field(name="現在指定されているバナー名：", value=banner_name)
        embed.add_field(name="現在引いた回数：", value=f"{str(self.roof)} 回")
        embed.set_image(
            url=f'https://cdn.discordapp.com/attachments/1034136716862296114/{image_id}/unknown.png')
        return embed


class Wish_bataCog(commands.Cog):

    def __init__(self, bot):
        print('wish初期化.')
        self.bot = bot

    def embeded(title, description, url):
        embed = discord.Embed(title=title, color=0x1e90ff,
                              description=description)
        embed.set_image(url=url)
        return embed

    wish = SlashCommandGroup('wish_bata', 'test')

    @wish.command(name="get", description="原神ガチャシミュレーター")
    async def get(
            self,
            ctx: discord.ApplicationContext):

        await ctx.respond(content="えらぶんだもん", view=wish_banner_select_View())

    @wish.command(name="get_image", description="ガチャイラスト取得")
    async def get_image(
        self,
        ctx: discord.ApplicationContext,
        character_name: str,
    ):
        embed = discord.Embed(title=character_name, color=0x1e90ff)
        embed.set_image(url=name_to_url[character_name])
        await ctx.respond(content=character_name, embed=embed)


class wish_main_system_value():
    def __init__(self, id, banner_id, roof, resalt, final_resalt):
        self.id = id
        self.banner_id = banner_id
        self.roof = roof
        self.resalt = resalt
        self.final_resalt = final_resalt


def get_wish_display_embed(character_name: str, ster):
    if "3" == ster:
        color = 0x1e90ff
    elif "4" == ster:
        color = 0x8a2be2
    elif "5" or "6" == ster:
        color = 0xff8c00
    embed = discord.Embed(title=character_name, color=color)
    embed.set_image(url=name_to_url[character_name])
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
        現在のあなたの天井値: **{roof}**
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
        url=f"https://cdn.discordapp.com/attachments/1034136716862296114/{banner_data['image']}/unknown.png")
    return embed


class wish_banner_select_View(View):
    def __init__(self):
        super().__init__(timeout=300, disable_on_timeout=True)

    @discord.ui.select(
        placeholder="ガチャを指定（~ver1.6）",
        options=get_wish_select_options()[0]
    )
    async def select_callback_1(self, select: discord.ui.Select, interaction: discord.Interaction):
        view = wish_select_View(banner_id=int(select.values[0]))
        print(
            f"実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nver1.6")
        await interaction.response.edit_message(content=f"祈願回数を指定してください。", embed=get_banner_embed(int(select.values[0])), view=view)

    @discord.ui.select(
        placeholder="ガチャを指定（~ver2.8）",
        options=get_wish_select_options()[1]
    )
    async def select_callback_2(self, select: discord.ui.Select, interaction: discord.Interaction):
        view = wish_select_View(banner_id=int(select.values[0]))
        print(
            f"実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nver2.8")
        await interaction.response.edit_message(content=f"祈願回数を指定してください。", embed=get_banner_embed(int(select.values[0])), view=view)

    @discord.ui.select(
        placeholder="ガチャを指定（ver3.0~）",
        options=get_wish_select_options()[2]
    )
    async def select_callback_3(self, select: discord.ui.Select, interaction: discord.Interaction):
        view = wish_select_View(banner_id=int(select.values[0]))
        print(
            f"実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nver3.0")
        await interaction.response.edit_message(content=f"祈願回数を指定してください。", embed=get_banner_embed(int(select.values[0])), view=view)


class wish_select_View(View):
    def __init__(self, banner_id: int):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.banner_id = banner_id

    @discord.ui.button(label="1回")
    async def once(self, _: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="ローディング", view=None)
        await get_wish_resalt(interaction, 1, self.banner_id)

    @discord.ui.button(label="10回")
    async def twice(self, _: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="ローディング", view=None)
        await get_wish_resalt(interaction, 10, self.banner_id)

    @discord.ui.button(label="回数指定")
    async def enter(self, _: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(modal=select_wish_modal(interaction, self.banner_id))


class select_wish_modal(discord.ui.Modal):
    def __init__(self, interaction, banner_id):
        super().__init__(title="あなたのUIDを入力してください。", timeout=300,)
        self.interaction = interaction
        self.banner_id = banner_id

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
            print(hoge)
            if hoge > 100:
                raise
            await get_wish_resalt(self.interaction, hoge, self.banner_id)
        except:
            await interaction.edit_original_message(content="入力された数値が無効です。", view=None)


async def get_wish_resalt(interaction: discord.Interaction, num, banner_id):
    id = interaction.user.id
    # まずこいつの天井、指定バナーを取得
    roofGet(id, 0)
    wishData = roofInit()
    roof = wishData[id]["roof"]

    # とりあえず天井から結果num回を排出
    await interaction.edit_original_message(content="ガチャ結果読み込み中...")
    resalt = []
    for n in range(num):
        resalt.append(wish_list(roof=roof, id=id))
        roof = roofGet(id, 1)
    random.shuffle(resalt)

    # 結果からキャラ名に変換
    await interaction.edit_original_message(content="ガチャ画面読み込み中...")
    final_resalt = []
    for ster in resalt:
        final_resalt.append(number_to_character(ster, banner_id))

    # 全部の変数まとめ
    DATA = wish_main_system_value(
        id=id, banner_id=banner_id, roof=roof, resalt=resalt, final_resalt=final_resalt)

    await interaction.edit_original_message(content="演出画面読み込み中...")
    global is_skip_button_pressed
    is_skip_button_pressed = False
    # 条件分岐で画像変化
    view = View()
    view.add_item(WishSkipButton(interaction, DATA))
    if "5" in resalt or "6" in resalt:
        direction_embed = Wish_bataCog.embeded(
            None, None, "https://c.tenor.com/rOuL0G1uRpMAAAAC/genshin-impact-pull.gif")
        await interaction.edit_original_message(content=None, embed=direction_embed, view=view)
    else:
        direction_embed = Wish_bataCog.embeded(
            None, None, "https://c.tenor.com/pVzBgcp1RPQAAAAC/genshin-impact-animation.gif")
        await interaction.edit_original_message(content=None, embed=direction_embed, view=view)
    await asyncio.sleep(5.5)

    if is_skip_button_pressed == False:
        view = View()
        view.add_item(GotoNextButton(interaction, DATA, 1))
        view.add_item(GotoResultButton(interaction, DATA))
        print(DATA.resalt[0])
        await interaction.edit_original_message(content=None, embed=get_wish_display_embed(DATA.final_resalt[0], DATA.resalt[0]), view=view)


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
        view.add_item(GotoNextButton(self.interaction, self.DATA, 1))
        view.add_item(GotoResultButton(self.interaction, self.DATA))
        await interaction.response.edit_message(content=None, embed=get_wish_display_embed(self.DATA.final_resalt[0], self.DATA.resalt[0]), view=view)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nwish get - スキップ")

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
            await interaction.response.edit_message(content=None, embed=get_wish_display_embed(self.DATA.final_resalt[self.v], self.DATA.resalt[self.v]), view=view)
        else:
            await interaction.response.edit_message(content="読み込み中...", embed=None, view=None)
            view = View()
            view.add_item(Wish_again_Button(
                self.interaction, self.DATA))
            await interaction.edit_original_message(content=None, embed=get_wish_resalt_display_embed(self.DATA), view=view)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nwish get - スキップ")

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
        await interaction.edit_original_message(content=None, embed=get_wish_resalt_display_embed(self.DATA), view=view)

# もう一回遊べるどん


class Wish_again_Button(discord.ui.Button):
    def __init__(self, interaction, DATA: wish_main_system_value):
        super().__init__(label="もう一度祈願する", style=discord.ButtonStyle.green)
        self.interaction = interaction
        self.DATA = DATA

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="ローディング", view=None)
        await get_wish_resalt(interaction, len(self.DATA.resalt), self.DATA.banner_id)


def setup(bot):
    bot.add_cog(Wish_bataCog(bot))
