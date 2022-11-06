from webbrowser import get
from lib.yamlutil import yaml
import discord
from discord.ext import commands
from discord import Option, OptionChoice, SlashCommandGroup
from discord.ui import View
import random
import urllib
import asyncio

is_skip_button_pressed = False

# ファイル指定
wishYaml = yaml('wish.yaml')
genshinYaml = yaml('genshin.yaml')
genshinHYaml = yaml('genshinH.yaml')
genshinStarYaml = yaml('genshin_ster.yaml')

# ファイル初期化
wishData = wishYaml.load_yaml()
characterName = genshinYaml.load_yaml()
characterTrans = genshinHYaml.load_yaml()
bannerData = genshinStarYaml.load_yaml()


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
    print(per)
    print(three)
    print(five)

    if roof == 180:
        # 二度目の天井。確定で6を追加。ついでに天井リセット。
        tmpresalt = ["6"]
        roofReset(id, 0)

    elif roof == 90:
        # 一度目の天井に達した確率。2/1の確率で5か6を追加。
        tmpresalt = random.choices(["5", "6"], weights=[0.5, 0.5])
        if "6" in tmpresalt:  # 6が出た場合は天井リセットです。
            roofReset(id, 0)
        return tmpresalt

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

        id = ctx.author.id

        # 何か送信しないと応答なしと判断されてエラーを吐くので一応
        foo = await ctx.respond("処理を開始中...")

        # まずこいつの天井、指定バナーを取得
        roofGet(id, 0)
        wishData = roofInit()
        roof = wishData[id]["roof"]
        banner = wishData[id]["banner"]

        # とりあえず天井から結果10回を排出
        resalt = []
        for n in range(10):
            resalt.append(wish_list(roof=roof, id=id))
            roof = roofGet(id, 1)
            print(resalt)
        random.shuffle(resalt)

        print(type(foo))
        global is_skip_button_pressed
        is_skip_button_pressed = False
        # 条件分岐で画像変化
        view = View()
        view.add_item(WishSkipButton(ctx, resalt))
        if "5" in resalt or "6" in resalt:
            direction_embed = Wish_bataCog.embeded(
                None, None, "https://c.tenor.com/rOuL0G1uRpMAAAAC/genshin-impact-pull.gif")
            await foo.edit_original_message(content=None, embed=direction_embed, view=view)
        else:
            direction_embed = Wish_bataCog.embeded(
                None, None, "https://c.tenor.com/pVzBgcp1RPQAAAAC/genshin-impact-animation.gif")
            await foo.edit_original_message(content=None, embed=direction_embed, view=view)
        await asyncio.sleep(5.5)

        if is_skip_button_pressed == False:
            ster = resalt[0]
            view = View()
            view.add_item(GotoNextButton(ctx, resalt, 1))
            view.add_item(GotoResultButton(ctx, resalt))
            await foo.edit_original_message(content=ster, embed=None, view=view)


# スキップボタンを表示させるボタン
class WishSkipButton(discord.ui.Button):
    def __init__(self, ctx, resalt):
        super().__init__(label="スキップ", style=discord.ButtonStyle.green)
        self.ctx = ctx
        self.resalt = resalt

    async def callback(self, interaction: discord.Interaction):
        global is_skip_button_pressed
        is_skip_button_pressed = True
        ster = self.resalt[0]
        view = View()
        view.add_item(GotoNextButton(self.ctx, self.resalt, 1))
        view.add_item(GotoResultButton(self.ctx, self.resalt))
        await interaction.response.edit_message(content=ster, embed=None, view=view)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nwish get - スキップ")

# 次のボタンを表示させるボタン


class GotoNextButton(discord.ui.Button):
    def __init__(self, ctx, resalt, v):
        super().__init__(label="続ける", style=discord.ButtonStyle.green)
        self.ctx = ctx
        self.resalt = resalt
        self.v = v

    async def callback(self, interaction: discord.Interaction):
        if self.v < 9:
            ster = self.resalt[self.v]
            self.v += 1
            view = View()
            view.add_item(GotoNextButton(self.ctx, self.resalt, self.v))
            view.add_item(GotoResultButton(self.ctx, self.resalt))
            await interaction.response.edit_message(content=ster, embed=None, view=view)
        else:
            await interaction.response.edit_message(content=self.resalt, embed=None, view=None)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nwish get - スキップ")

# 全部飛ばすボタン


class GotoResultButton(discord.ui.Button):
    def __init__(self, ctx, resalt):
        super().__init__(label="結果を見る", style=discord.ButtonStyle.green)
        self.ctx = ctx
        self.resalt = resalt

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=self.resalt, embed=None, view=None)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nwish get - スキップ")


def setup(bot):
    bot.add_cog(Wish_bataCog(bot))
