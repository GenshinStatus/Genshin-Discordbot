import discord
import aiohttp
from lib.yamlutil import yaml
import lib.scoreCalculator as genshinscore
from typing import List
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests
import urllib
import datetime
import os

chara = None

charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinTextHash = genshinJpYaml.load_yaml()
wordsYaml = yaml(path='genshin.yaml')
words = wordsYaml.load_yaml()

ConfigYaml = yaml(path='genshinDataConfig.yaml')
config = ConfigYaml.load_yaml()

async def get(uid,id):
    final_resalt = {}
    url = f"https://enka.network/u/{uid}/__data.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.json()
    name = characters[id]["NameId"]
    name = genshinTextHash[name]
    final_resalt["characterName"] = name
    id = int(id)
    try:
        #アバターインフォリストを回す。nにキャラ情報がすべて入る。
        for n in resp['avatarInfoList']:
            if n["avatarId"] == id:
                chara = n
                break
            else:
                continue
    except:
        embed = discord.Embed( 
            title="エラー",
            color=0x1e90ff,
            description=f"キャラ詳細が非公開です。原神の設定で公開設定にしてください。", 
            url=url 
        )
        return embed
    try:
        level = chara["propMap"]["4001"]["val"]
        final_resalt["level"] = level
        embed = discord.Embed( 
                    title=name,
                    color=0x1e90ff, 
                    description=f"{level}lv", 
                    url=url 
                    )
        sideIcon = characters[str(id)]["sideIconName"]
        embed.set_thumbnail(url=f"https://enka.network/ui/{sideIcon}.png")

        embed.add_field(inline=True,name="キャラレベル",value=f"{level}lv")
        embed.add_field(inline=True,name="キャラ突破レベル",value=str(chara["propMap"]["1002"]["ival"]))
        embed.add_field(inline=True,name="HP",
            value=f'{str(round(chara["fightPropMap"]["1"]))} + {str(round(chara["fightPropMap"]["2000"]) - round(chara["fightPropMap"]["1"]))} = {str(round(chara["fightPropMap"]["2000"]))}'
        )
        embed.add_field(inline=True,name="攻撃力",
            value=f'{str(round(chara["fightPropMap"]["4"]))} + {str(round(chara["fightPropMap"]["2001"]) - round(chara["fightPropMap"]["4"]))} = {str(round(chara["fightPropMap"]["2001"]))}'
        )
        embed.add_field(inline=True,name="防御力",
            value=f'{str(round(chara["fightPropMap"]["7"]))} + {str(round(chara["fightPropMap"]["2002"]) - round(chara["fightPropMap"]["7"]))} = {str(round(chara["fightPropMap"]["2002"]))}'
        )
        embed.add_field(inline=True,name="会心率",
            value=f'{str(round(chara["fightPropMap"]["20"] *100))}%'
        )
        embed.add_field(inline=True,name="会心ダメージ",
            value=f'{str(round(chara["fightPropMap"]["22"]*100))}%'
        )
        embed.add_field(inline=True,name="元素チャージ効率",
            value=f'{str(round(chara["fightPropMap"]["23"]*100))}%'
        )
        embed.add_field(inline=True,name="元素熟知",
            value=f'{str(round(chara["fightPropMap"]["28"]))}'
        )
        buf = 1
        if round(chara["fightPropMap"]["30"]*100) > 0:
            embed.add_field(inline=True,name="物理ダメージ",
                value=f'{str(round(chara["fightPropMap"]["30"]*100))}%'
            )
            buf += round(chara["fightPropMap"]["30"])
        elif round(chara["fightPropMap"]["40"]*100) > 0:
            embed.add_field(inline=True,name="炎元素ダメージ",
                value=f'{str(round(chara["fightPropMap"]["40"]*100))}%'
            )
            buf += round(chara["fightPropMap"]["40"])
        elif round(chara["fightPropMap"]["41"]*100) > 0:
            embed.add_field(inline=True,name="雷元素ダメージ",
                value=f'{str(round(chara["fightPropMap"]["41"]*100))}%'
            )
            buf += round(chara["fightPropMap"]["41"])
        elif round(chara["fightPropMap"]["42"]*100) > 0:
            embed.add_field(inline=True,name="水元素ダメージ",
                value=f'{str(round(chara["fightPropMap"]["42"]*100))}%'
            )
            buf += round(chara["fightPropMap"]["42"])
        elif round(chara["fightPropMap"]["43"]*100) > 0:
            embed.add_field(inline=True,name="草元素ダメージ",
                value=f'{str(round(chara["fightPropMap"]["43"]*100))}%'
            )
            buf += round(chara["fightPropMap"]["42"])
        elif round(chara["fightPropMap"]["44"]*100) > 0:
            embed.add_field(inline=True,name="風元素ダメージ",
                value=f'{str(round(chara["fightPropMap"]["44"]*100))}%'
            )
            buf += round(chara["fightPropMap"]["44"])
        elif round(chara["fightPropMap"]["45"]*100) > 0:
            embed.add_field(inline=True,name="岩元素ダメージ",
                value=f'{str(round(chara["fightPropMap"]["45"]*100))}%'
            )
            buf += round(chara["fightPropMap"]["45"])
        elif round(chara["fightPropMap"]["46"]*100) > 0:
            embed.add_field(inline=True,name="氷元素ダメージ",
                value=f'{str(round(chara["fightPropMap"]["46"]*100))}%'
            )
            buf += round(chara["fightPropMap"]["46"])
        temp = []
        for myvalue in chara["skillLevelMap"].values():
            temp.append(f"{myvalue}")
        embed.add_field(inline=False,name="天賦レベル",
            value="\n".join(temp)
        )

        #ここから聖遺物とかを回す
        for n in chara["equipList"]:
            hoge = []
            statscore = []
            #print(f"{n}\n\n")
            if 'weapon' in n:
                level = n["weapon"]["level"]
                name = genshinTextHash[n["flat"]["nameTextMapHash"]]
                resalt = f"{level}lv\n{name}\n"
                for weapon in n["flat"]["weaponStats"]:
                    main_name = genshinTextHash[weapon["appendPropId"]]
                    main_value = "".join(str([weapon["statValue"]]))
                    resalt += f"**{main_name}** : {main_value}\n"
                embed.add_field(inline=True,name=f'武器',
                value=resalt
                )
            else:
                name = genshinTextHash[n["flat"]["setNameTextMapHash"]]
                equip = genshinTextHash[n["flat"]["equipType"]]
                main = genshinTextHash[n["flat"]["reliquaryMainstat"]["mainPropId"]]
                for b in n["flat"]["reliquarySubstats"]:
                    name_ = genshinTextHash[b["appendPropId"]]
                    value_ = b["statValue"]
                    hoge.append(f"{name_}：{value_}")
                    statscore.append({name_:value_})
                getscore = {main:n["flat"]["reliquaryMainstat"]["statValue"]}
                embed.add_field(inline=True,name=f'聖遺物：{equip}\n{name}\n{main}：{n["flat"]["reliquaryMainstat"]["statValue"]}\n{n["reliquary"]["level"]-1}lv\n聖遺物スコア：**{await genshinscore.score(statscore,getscore)}**\n',
                    value="\n".join(hoge)
                )
            embed.set_footer(text="ボタンは連続リクエストを防ぐため、一定時間後に無効化されます。ご了承ください。")
        return embed
    except KeyError:
        raise
        return embed

def downloadPicture(url):
    now = datetime.datetime.now()
    time_now = "{0:%Y%m%d_%H%M-%S_%f}".format(now)
    file_name = f"{time_now}.png"
    response = requests.get(url)
    image = response.content

    with open(f"C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\{file_name}", "wb") as aaa:
        aaa.write(image)
    return f"C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\{file_name}"

def add_text_to_image(img, text, font_size, font_color, height, width, max_length=740):
    position = (width, height)
    font = ImageFont.truetype(font="C:\\Users\\Cinnamon\\AppData\\Local\\Microsoft\\Windows\\Fonts\\ja-jp.ttf",size=font_size)
    draw = ImageDraw.Draw(img)
    if draw.textsize(text, font=font)[0] > max_length:
        while draw.textsize(text + '…', font=font)[0] > max_length:
            text = text[:-1]
        text = text + '…'

    draw.text(position, text, font_color, font=font)
    return img

def getCharacterPicture(name):
    global words
    global genshinTextHash
    hoge = []
    hoge.append(name)
    if name in ["コレイ","ティナリ"]:
        return words[name]["url"]
    if name in words:
        resalt = urllib.parse.quote(words[name]["zh"])
    elif name in genshinTextHash:
        resalt = urllib.parse.quote(words[genshinTextHash[name]["ja"]]["zh"])
    else:
        resalt = None
    return f"https://bbs.hoyolab.com/hoyowiki/picture/character/{resalt}/avatar.png"

async def getCharacterImage(uid,id):
    url = f"https://enka.network/u/{uid}/__data.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.json()
    name = characters[id]["NameId"]
    name = genshinTextHash[name]
  
    #プロフィールアイコン取得
    temp_1 = downloadPicture(getCharacterPicture(name))
    icon = Image.open(temp_1).convert('RGBA').copy()
    #プロフィールアイコンのリサイズ
    icon = icon.resize(size=(icon.width//3, icon.height//3), resample=Image.ANTIALIAS)

    #背景画像読み込み
    base_img = Image.open(f"C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\status\\{config[str(id)]['Element']}.png").convert('RGBA').copy()
    #バグ対策に背景を完全透過させたものを生成
    base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    #base_img.paste(icon, (80, 134), icon)

    #アイコン合成
    #背景の画像サイズを/2して中心座標を取得したものから、アイコンのサイズ/2を引く
    width,height = base_img.size
    width = width//2 - icon.width//2
    height = height//2 - icon.height//2
    #バグ対策背景画像にアルファ合成
    base_img_clear.paste(icon, (width-50, height))
    #バグ対策できたんでちゃんと合成
    base_img = Image.alpha_composite(base_img, base_img_clear)

    #☆追加
    icon = Image.open("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\ster.png").convert('RGBA').copy()
    icon = icon.resize(size=(icon.width//2, icon.height//2), resample=Image.ANTIALIAS)
    base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    #バグ対策背景画像にアルファ合成
    for n in range(words[name]["ster"]):
        base_img_clear.paste(icon, (35+n*20, 70))
    #バグ対策できたんでちゃんと合成
    base_img = Image.alpha_composite(base_img, base_img_clear)

    #ユーザー名文字追加
    player_name = name
    font_size = 45
    font_color = (255, 255, 255)
    height = 20
    width = 35
    img = add_text_to_image(base_img, player_name, font_size, font_color, height, width)

    try:
        #アバターインフォリストを回す。nにキャラ情報がすべて入る。
        for n in resp['avatarInfoList']:
            if n["avatarId"] == int(id):
                chara = n
                break
            else:
                print("hoihoi")
                continue
    except:
        embed = discord.Embed( 
            title="エラー",
            color=0x1e90ff,
            description=f"キャラ詳細が非公開です。原神の設定で公開設定にしてください。", 
            url=url 
        )
        return embed
    try:
        for n in resp['avatarInfoList']:
            if n["avatarId"] == int(id):
                chara = n
                print(chara)
                break
            else:
                continue
        #レベル文字追加
        player_name = f'{chara["propMap"]["4001"]["val"]}Lv'
        font_size = 12
        font_color = (255, 255, 255)
        height = 70
        width = 145
        img = add_text_to_image(base_img, player_name, font_size, font_color, height, width)

        embed = discord.Embed( 
                    title=name,
                    color=0x1e90ff, 
                    description=f'{chara["propMap"]["4001"]["val"]}lv', 
                    url=url 
                    )
        sideIcon = characters[str(id)]["sideIconName"]
        embed.set_thumbnail(url=f"https://enka.network/ui/{sideIcon}.png")

        #HP基礎　文字追加
        player_name = str(round(chara["fightPropMap"]["1"]))
        font_size = 10
        font_color = (255, 255, 255)
        height = 115
        width = 100
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #HP聖遺物　文字追加
        player_name = f'+{str(round(chara["fightPropMap"]["2000"]) - round(chara["fightPropMap"]["1"]))}'
        font_size = 10
        font_color = (169, 255, 0)
        height = 115
        width = 135
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #HP合計値　文字追加
        player_name = str(round(chara["fightPropMap"]["2000"]))
        font_size = 16
        font_color = (118, 255, 255)
        height = 95
        width = 110
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        
        
        #攻撃力基礎　文字追加
        player_name = str(round(chara["fightPropMap"]["4"]))
        font_size = 10
        font_color = (255, 255, 255)
        height = 152
        width = 100
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #攻撃力聖遺物　文字追加
        player_name = f'+ {str(round(chara["fightPropMap"]["2001"]) - round(chara["fightPropMap"]["4"]))}'
        font_size = 10
        font_color = (169, 255, 0)
        height = 152
        width = 135
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #攻撃力合計値　文字追加
        player_name = str(round(chara["fightPropMap"]["2001"]))
        font_size = 16
        font_color = (118, 255, 255)
        height = 132
        width = 110
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        
        
        #防御力基礎　文字追加
        player_name = str(round(chara["fightPropMap"]["7"]))
        font_size = 10
        font_color = (255, 255, 255)
        height = 192
        width = 100
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #防御力聖遺物　文字追加
        player_name = f'+ {str(round(chara["fightPropMap"]["2002"]) - round(chara["fightPropMap"]["7"]))}'
        font_size = 10
        font_color = (169, 255, 0)
        height = 192
        width = 135
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #防御力合計値　文字追加
        player_name = str(round(chara["fightPropMap"]["2002"]))
        font_size = 16
        font_color = (118, 255, 255)
        height = 172
        width = 110
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        
        
        #会心率　文字追加
        player_name = f'{str(round(chara["fightPropMap"]["20"] *100))}%'
        font_size = 16
        font_color = (118, 255, 255)
        height = 217
        width = 110
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #会心ダメ　文字追加
        player_name = f'{str(round(chara["fightPropMap"]["22"] *100))}%'
        font_size = 16
        font_color = (118, 255, 255)
        height = 255
        width = 110
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #元素チャージ　文字追加
        player_name = f'{str(round(chara["fightPropMap"]["23"] *100))}%'
        font_size = 16
        font_color = (118, 255, 255)
        height = 292
        width = 110
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        #元素熟知　文字追加
        player_name = str(round(chara["fightPropMap"]["28"]))
        font_size = 16
        font_color = (118, 255, 255)
        height = 332
        width = 110
        img = add_text_to_image(img, player_name, font_size, font_color, height, width)

        buf = 1
        if round(chara["fightPropMap"]["30"]*100) > 0:
            propname="物理ダメージ",
            value=f'{str(round(chara["fightPropMap"]["30"]*100))}%'
            buf += round(chara["fightPropMap"]["30"])
        elif round(chara["fightPropMap"]["40"]*100) > 0:
            propname="炎元素ダメージ",
            value=f'{str(round(chara["fightPropMap"]["40"]*100))}%'
            buf += round(chara["fightPropMap"]["40"])
        elif round(chara["fightPropMap"]["41"]*100) > 0:
            propname="雷元素ダメージ",
            value=f'{str(round(chara["fightPropMap"]["41"]*100))}%'
            buf += round(chara["fightPropMap"]["41"])
        elif round(chara["fightPropMap"]["42"]*100) > 0:
            propname="水元素ダメージ",
            value=f'{str(round(chara["fightPropMap"]["42"]*100))}%'
            buf += round(chara["fightPropMap"]["42"])
        elif round(chara["fightPropMap"]["43"]*100) > 0:
            propname="草元素ダメージ",
            value=f'{str(round(chara["fightPropMap"]["43"]*100))}%'
            buf += round(chara["fightPropMap"]["42"])
        elif round(chara["fightPropMap"]["44"]*100) > 0:
            propname="風元素ダメージ",
            value=f'{str(round(chara["fightPropMap"]["44"]*100))}%'
            buf += round(chara["fightPropMap"]["44"])
        elif round(chara["fightPropMap"]["45"]*100) > 0:
            propname="岩元素ダメージ",
            value=f'{str(round(chara["fightPropMap"]["45"]*100))}%'
            buf += round(chara["fightPropMap"]["45"])
        elif round(chara["fightPropMap"]["46"]*100) > 0:
            propname="氷元素ダメージ",
            value=f'{str(round(chara["fightPropMap"]["46"]*100))}%'
            buf += round(chara["fightPropMap"]["46"])

        hogehoge = 0
        for skill in config[id]['SkillOrder']:
            hogehoge+=1
            #天賦アイコン追加
            temp_2 = downloadPicture(f"https://enka.network/ui/{config[id]['Skills'][str(skill)]}.png")
            icon = Image.open(temp_2).convert('RGBA').copy()
            icon = icon.resize(size=(48, 48), resample=Image.ANTIALIAS)
            base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
            #バグ対策背景画像にアルファ合成
            base_img_clear.paste(icon, (650, -50+hogehoge*70))
            #バグ対策できたんでちゃんと合成
            img = Image.alpha_composite(img, base_img_clear)

        img.save('C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\2.png')
        os.remove("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture")
        return "C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\2.png"

        temp = []
        for myvalue in chara["skillLevelMap"].values():
            temp.append(f"{myvalue}")
        embed.add_field(inline=False,name="天賦レベル",
            value="\n".join(temp)
        )

        #ここから聖遺物とかを回す
        for n in chara["equipList"]:
            hoge = []
            statscore = []
            #print(f"{n}\n\n")
            if 'weapon' in n:
                level = n["weapon"]["level"]
                name = genshinTextHash[n["flat"]["nameTextMapHash"]]
                resalt = f"{level}lv\n{name}\n"
                for weapon in n["flat"]["weaponStats"]:
                    main_name = genshinTextHash[weapon["appendPropId"]]
                    main_value = "".join(str([weapon["statValue"]]))
                    resalt += f"**{main_name}** : {main_value}\n"
                embed.add_field(inline=True,name=f'武器',
                value=resalt
                )
            else:
                name = genshinTextHash[n["flat"]["setNameTextMapHash"]]
                equip = genshinTextHash[n["flat"]["equipType"]]
                main = genshinTextHash[n["flat"]["reliquaryMainstat"]["mainPropId"]]
                for b in n["flat"]["reliquarySubstats"]:
                    name_ = genshinTextHash[b["appendPropId"]]
                    value_ = b["statValue"]
                    hoge.append(f"{name_}：{value_}")
                    statscore.append({name_:value_})
                getscore = {main:n["flat"]["reliquaryMainstat"]["statValue"]}
                embed.add_field(inline=True,name=f'聖遺物：{equip}\n{name}\n{main}：{n["flat"]["reliquaryMainstat"]["statValue"]}\n{n["reliquary"]["level"]-1}lv\n聖遺物スコア：**{await genshinscore.score(statscore,getscore)}**\n',
                    value="\n".join(hoge)
                )
            embed.set_footer(text="ボタンは連続リクエストを防ぐため、一定時間後に無効化されます。ご了承ください。")
        return embed
    except KeyError:
        raise
        return embed