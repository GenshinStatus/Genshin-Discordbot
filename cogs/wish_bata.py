from lib.yamlutil import yaml
import discord
from discord.ext import commands
from discord import Option, OptionChoice, SlashCommandGroup
import random
import urllib
import asyncio


#ファイル指定
wishYaml = yaml('wish.yaml')
genshinYaml = yaml('genshin.yaml')
genshinHYaml = yaml('genshinH.yaml')
genshinStarYaml = yaml('genshin_ster.yaml')

#ファイル初期化
wishData = wishYaml.load_yaml()
characterName = genshinYaml.load_yaml()
characterTrans = genshinHYaml.load_yaml()
bannerData = genshinStarYaml.load_yaml()

def roofInit():
    wishYaml = yaml('wish.yaml')
    wishData = wishYaml.load_yaml()
    return wishData

changed_per=[20.627, 13.946, 9.429, 6.375, 4.306, 2.914, 1.970, 1.332,0.901,0.608,0.411,0.278,0.187,0.126,0.265]

def getPer(roof:int):
    '''
    現在の天井から確率を出してくれるいい奴
    '''
    one_roof=roof%90
    if one_roof==0:
        hoge= changed_per[-1]
    elif one_roof<=75:
        hoge= 0.603-0.003*one_roof
    else:
        hoge= changed_per[roof-76]
    return hoge/100

def roofReset(id:int,roof:int):
    '''
    指定した天井の数値にするよ
    '''
    hoge = roofInit()
    hoge[id] = {"roof": roof, "banner":hoge[id]["banner"], "num":hoge[id]["num"]}
    wishYaml.save_yaml(hoge)
    return

def roofGet(id:int,roof:int):
    '''
    idから天井を足して結果をintで返すよ
    '''
    hoge = roofInit()
    if id in hoge:
        roof += hoge[id]["roof"]
        banner = hoge[id]["banner"]
        num = hoge[id]["num"]
    else:
        roof += 0
        banner = 00000
        num = 0
    hoge[id] = {"roof": roof, "banner": banner, "num": num}
    wishYaml.save_yaml(hoge)
    return roof

def genshingen(name:str):
    '''
    名前（日本語名）からキャラの画像urlを返すよ
    '''
    if name in ["コレイ","ティナリ","旅人","ニィロウ","キャンディス","セノ"]:
        return characterName[name]["url"]
    if name in characterName:
        resalt = urllib.parse.quote(characterName[name]["zh"])
    elif name in characterTrans:
        resalt = urllib.parse.quote(characterName[characterTrans[name]["ja"]]["zh"])
    else:
        resalt = None
    return f"https://bbs.hoyolab.com/hoyowiki/picture/character/{resalt}/avatar.png"

def wish_list(roof:int, id:int):
    '''
    キャラを排出します
    '''
    # 天井から確率を計算
    per = getPer(roof)
    three = 1 - per - 0.051 #星5が出ない確率 - 星4が出る確率
    five = per / 2 #すり抜け分です
    print(per)
    print(three)
    print(five)

    if roof == 180:
        # 二度目の天井。確定で6を追加。ついでに天井リセット。
        tmpresalt = ["6"]
        roofReset(id,0)

    elif roof == 90:
        # 一度目の天井に達した確率。2/1の確率で5か6を追加。
        tmpresalt = random.choices(["5", "6"], weights=[0.5, 0.5])
        if "6" in tmpresalt: # 6が出た場合は天井リセットです。
            roofReset(id,0)
        return tmpresalt

    elif roof % 10 > 0:
        # 通常の確率。
        tmpresalt = random.choices(["3", "4", "5", "6"], weights=[three, 0.051, five, five])
        if "5" in tmpresalt: # 星5が出た場合は、星5が出なくなる天井カウント90に、
            roofReset(id,90)
        elif "6" in tmpresalt: # 星6が出た場合は天井カウントをリセットします。
            roofReset(id,0)

    elif roof % 10 == 0:
        # 星4天井システム。必ず星4以上を追加します。
        tmpresalt = random.choices(["3", "4", "5", "6"], weights=[
                                    three, 0.051, five, five])
        if "5" in tmpresalt: # 星5が出た場合は、星5が出なくなる天井カウント90に、
            roofReset(id,90)
        elif "6" in tmpresalt: # 星6が出た場合は天井カウントをリセットします。
            roofReset(id,0)
        else:
            tmpresalt = ["4"]

    if roof > 90:
        # 一度目の天井以降の確率。5は出ない。
        if "5" in tmpresalt: # 5の場合6にし、天井と確率リセット。
            tmpresalt = ["6"]
            roofReset(id,0)

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
    
    wish = SlashCommandGroup('wish_bata', 'test')

    @wish.command(name="get", description="原神ガチャシミュレーター")
    async def get(
        self,
        ctx: discord.ApplicationContext):
        
        id = ctx.author.id
        name = ctx.author.name

        # 何か送信しないと応答なしと判断されてエラーを吐くので一応
        await ctx.respond("処理を開始中...", ephemeral=True)

        #まずこいつの天井、指定バナーを取得
        roofGet(id,0)
        wishData = roofInit()
        roof = wishData[id]["roof"]
        banner = wishData[id]["banner"]
        
        #とりあえず天井から結果10回を排出
        resalt = []
        for n in range(10):
            resalt.append(wish_list(roof=roof,id=id))
            roof = roofGet(id,1)

        await ctx.respond(resalt)

def setup(bot):
    bot.add_cog(Wish_bataCog(bot))