import discord
import aiohttp
from lib.yamlutil import yaml
import lib.scoreCalculator as genshinscore
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import requests
import urllib
import datetime
import random
import os
import shutil

chara = None

charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinTextHash = genshinJpYaml.load_yaml()
wordsYaml = yaml(path='genshin.yaml')
words = wordsYaml.load_yaml()

ConfigYaml = yaml(path='genshinDataConfig.yaml')
config = ConfigYaml.load_yaml()


def downloadPicture(url):
    now = datetime.datetime.now()
    time_now = "{0:%Y%m%d_%H%M-%S_%f}".format(now)
    file_name = f"{time_now}.png"
    response = requests.get(url)
    image = response.content

    with open(f"temp/{file_name}", "wb") as aaa:
        aaa.write(image)
    return f"temp/{file_name}"


def add_text_to_image(img, text, font_size, font_color, height, width, max_length=740, anchor=None):
    position = (width, height)
    font = ImageFont.truetype(
        font="C:\\Users\\Cinnamon\\AppData\\Local\\Microsoft\\Windows\\Fonts\\ja-jp.ttf", size=font_size)
    draw = ImageDraw.Draw(img)
    if draw.textsize(text, font=font)[0] > max_length:
        while draw.textsize(text + '…', font=font)[0] > max_length:
            text = text[:-1]
        text = text + '…'

    draw.text(position, text, font_color, font=font, anchor=anchor)
    return img


def getCharacterPicture(name):
    global words
    global genshinTextHash
    try:
        resalt = urllib.parse.quote(words[name]["zh"])
    except:
        try:
            return words[name]["url"]
        except:
            try:
                resalt = urllib.parse.quote(
                    words[genshinTextHash[name]["ja"]]["zh"])
            except:
                resalt = None
    return f"https://bbs.hoyolab.com/hoyowiki/picture/character/{resalt}/avatar.png"


def mask_circle_transparent(pil_img, blur_radius, offset=0):
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    result = pil_img.copy()
    result.putalpha(mask)

    return result


async def getCharacterImage(uid, id, interaction):
    url = f"https://enka.network/u/{uid}/__data.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.json()
    name = characters[id]["NameId"]
    name = genshinTextHash[name]

    # プロフィールアイコン取得
    temp_1 = downloadPicture(getCharacterPicture(name))
    icon = Image.open(temp_1).convert('RGBA').copy()
    # プロフィールアイコンのリサイズ
    s = 720/icon.height
    icon = icon.resize(size=(round(icon.width*s)+100,
                       round(icon.height*s)+100), resample=Image.ANTIALIAS)

    await interaction.edit_original_message(content="```準備中...```")
    # 背景画像読み込み
    base_img = Image.open(
        f"Image/status/{config[str(id)]['Element']}.png").convert('RGBA').copy()
    # バグ対策に背景を完全透過させたものを生成
    base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    #base_img.paste(icon, (80, 134), icon)

    # アイコン合成
    # 背景の画像サイズを/2して中心座標を取得したものから、アイコンのサイズ/2を引く
    width, height = base_img.size
    width = width//2 - icon.width//2
    height = height//2 - icon.height//2
    # バグ対策背景画像にアルファ合成
    base_img_clear.paste(icon, (width-300, height))
    # バグ対策できたんでちゃんと合成
    base_img = Image.alpha_composite(base_img, base_img_clear)

    # テキスト取得
    icon = Image.open("Image/status/base_text.png").convert('RGBA').copy()
    # バグ対策背景画像にアルファ合成
    base_img_clear.paste(icon, (0, 0))
    # バグ対策できたんでちゃんと合成
    base_img = Image.alpha_composite(base_img, base_img_clear)

    # ☆追加
    icon = Image.open("Image/ster.png").convert('RGBA').copy()
    icon = icon.resize(size=(icon.width//1, icon.height//1),
                       resample=Image.ANTIALIAS)
    base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    # バグ対策背景画像にアルファ合成
    for x in range(words[name]["ster"]):
        base_img_clear.paste(icon, (50+x*40, 130))
    # バグ対策できたんでちゃんと合成
    base_img = Image.alpha_composite(base_img, base_img_clear)

    await interaction.edit_original_message(content="```キャラ基本情報取得中...```")
    # ユーザー名文字追加
    player_name = name
    font_size = 88
    font_color = (255, 255, 255)
    height = 23
    width = 56
    img = add_text_to_image(base_img, player_name,
                            font_size, font_color, height, width)

    try:
        # アバターインフォリストを回す。nにキャラ情報がすべて入る。
        for n in resp['avatarInfoList']:
            if n["avatarId"] == int(id):
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
    for n in resp['avatarInfoList']:
        if n["avatarId"] == int(id):
            chara = n
            break
        else:
            continue

    try:
        hoge = chara["talentIdList"]
        hoge = str(len(hoge))
        print(hoge)
        if hoge == "6":
            hoge = "完"
        elif hoge == "0":
            hoge = "無"
    except:
        hoge = "無"
    # レベル文字追加
    player_name = f'{chara["propMap"]["4001"]["val"]}Lv  {hoge}凸'
    font_size = 24
    font_color = (255, 255, 255)
    height = 130
    width = 50+x*40+40
    img = add_text_to_image(base_img, player_name,
                            font_size, font_color, height, width)

    # HP基礎　文字追加
    player_name = str(round(chara["fightPropMap"]["1"]))
    font_size = 20
    font_color = (255, 255, 255)
    height = 211
    width = 200
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # HP聖遺物　文字追加
    player_name = f'+{str(round(chara["fightPropMap"]["2000"]) - round(chara["fightPropMap"]["1"]))}'
    font_size = 20
    font_color = (169, 255, 0)
    height = 211
    width = 270
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # HP合計値　文字追加
    player_name = str(round(chara["fightPropMap"]["2000"]))
    font_size = 32
    font_color = (118, 255, 255)
    height = 175
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力基礎　文字追加
    player_name = str(round(chara["fightPropMap"]["4"]))
    font_size = 20
    font_color = (255, 255, 255)
    height = 278
    width = 200
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力聖遺物　文字追加
    player_name = f'+ {str(round(chara["fightPropMap"]["2001"]) - round(chara["fightPropMap"]["4"]))}'
    font_size = 20
    font_color = (169, 255, 0)
    height = 278
    width = 270
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力合計値　文字追加
    player_name = str(round(chara["fightPropMap"]["2001"]))
    font_size = 32
    font_color = (118, 255, 255)
    height = 241
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力基礎　文字追加
    player_name = str(round(chara["fightPropMap"]["7"]))
    font_size = 20
    font_color = (255, 255, 255)
    height = 345
    width = 200
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力聖遺物　文字追加
    player_name = f'+ {str(round(chara["fightPropMap"]["2002"]) - round(chara["fightPropMap"]["7"]))}'
    font_size = 20
    font_color = (169, 255, 0)
    height = 345
    width = 270
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力合計値　文字追加
    player_name = str(round(chara["fightPropMap"]["2002"]))
    font_size = 32
    font_color = (118, 255, 255)
    height = 307
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 会心率　文字追加
    player_name = f'{str(round(chara["fightPropMap"]["20"] *100))}%'
    font_size = 32
    font_color = (118, 255, 255)
    height = 386
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 会心ダメ　文字追加
    player_name = f'{str(round(chara["fightPropMap"]["22"] *100))}%'
    font_size = 32
    font_color = (118, 255, 255)
    height = 446
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 元素チャージ　文字追加
    player_name = f'{str(round(chara["fightPropMap"]["23"] *100))}%'
    font_size = 32
    font_color = (118, 255, 255)
    height = 518
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 元素熟知　文字追加
    player_name = str(round(chara["fightPropMap"]["28"]))
    font_size = 32
    font_color = (118, 255, 255)
    height = 583
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    buf = 1
    propname = None
    value = None
    if round(chara["fightPropMap"]["30"]*100) > 0:
        propname = "物理ダメージ"
        value = f'{str(round(chara["fightPropMap"]["30"]*100))}%'
        buf += round(chara["fightPropMap"]["30"])
    elif round(chara["fightPropMap"]["40"]*100) > 0:
        propname = "炎元素ダメージ"
        value = f'{str(round(chara["fightPropMap"]["40"]*100))}%'
        buf += round(chara["fightPropMap"]["40"])
    elif round(chara["fightPropMap"]["41"]*100) > 0:
        propname = "雷元素ダメージ"
        value = f'{str(round(chara["fightPropMap"]["41"]*100))}%'
        buf += round(chara["fightPropMap"]["41"])
    elif round(chara["fightPropMap"]["42"]*100) > 0:
        propname = "水元素ダメージ"
        value = f'{str(round(chara["fightPropMap"]["42"]*100))}%'
        buf += round(chara["fightPropMap"]["42"])
    elif round(chara["fightPropMap"]["43"]*100) > 0:
        propname = "草元素ダメージ"
        value = f'{str(round(chara["fightPropMap"]["43"]*100))}%'
        buf += round(chara["fightPropMap"]["42"])
    elif round(chara["fightPropMap"]["44"]*100) > 0:
        propname = "風元素ダメージ"
        value = f'{str(round(chara["fightPropMap"]["44"]*100))}%'
        buf += round(chara["fightPropMap"]["44"])
    elif round(chara["fightPropMap"]["45"]*100) > 0:
        propname = "岩元素ダメージ"
        value = f'{str(round(chara["fightPropMap"]["45"]*100))}%'
        buf += round(chara["fightPropMap"]["45"])
    elif round(chara["fightPropMap"]["46"]*100) > 0:
        propname = "氷元素ダメージ"
        value = f'{str(round(chara["fightPropMap"]["46"]*100))}%'
        buf += round(chara["fightPropMap"]["46"])

    if propname != None:
        # 元素ダメバフ　文字追加
        player_name = propname
        font_size = 22
        font_color = (277, 185, 128)
        height = 655
        width = 38
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

        # 元素ダメバフ　文字追加
        player_name = value
        font_size = 32
        font_color = (118, 255, 255)
        height = 650
        width = 220
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

    await interaction.edit_original_message(content="```キャラ天賦情報取得中...```")
    hogehoge = 0
    for skill in config[id]['SkillOrder']:
        hogehoge += 1
        # 天賦アイコン追加
        temp_2 = downloadPicture(
            f"https://enka.network/ui/{config[id]['Skills'][str(skill)]}.png")
        icon = Image.open(temp_2).convert('RGBA').copy()
        icon = icon.resize(size=(96, 96), resample=Image.ANTIALIAS)
        base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
        # バグ対策背景画像にアルファ合成
        base_img_clear.paste(icon, (1100, -50+hogehoge*101))
        # バグ対策できたんでちゃんと合成
        img = Image.alpha_composite(img, base_img_clear)

    temp = []
    hogehoge = 0
    h = 0
    if len(chara["skillLevelMap"]) == 4:
        for myvalue in chara["skillLevelMap"].values():
            h += 1
            if h == 3:
                continue
            else:
                temp.append(f"{myvalue}")
    else:
        for myvalue in chara["skillLevelMap"].values():
            temp.append(f"{myvalue}")

    for level in temp:
        hogehoge += 1
        # 天賦　文字追加
        player_name = f"Lv.{level}"
        font_size = 40
        font_color = (255, 255, 255)
        height = -10+hogehoge*102
        width = 1215
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

    await interaction.edit_original_message(content="```キャラ聖遺物情報取得中...```")
    # ここから聖遺物とかを回す
    hogehoge = 0
    for n in chara["equipList"]:
        hoge = []
        statscore = []
        # print(f"{n}\n\n")
        if 'weapon' in n:
            # 武器アイコン追加
            temp_4 = downloadPicture(
                f'https://enka.network/ui/{n["flat"]["icon"]}.png')
            icon = Image.open(temp_4).convert('RGBA').copy()
            icon = icon.resize(size=(225, 225), resample=Image.ANTIALIAS)
            base_img_clear = Image.new(
                "RGBA", base_img.size, (255, 255, 255, 0))
            # バグ対策背景画像にアルファ合成
            base_img_clear.paste(icon, (1100, 505))
            # バグ対策できたんでちゃんと合成
            img = Image.alpha_composite(img, base_img_clear)

            cin = 1
            for weapon in n["flat"]["weaponStats"]:
                cin += 1
                main_name = genshinTextHash[weapon["appendPropId"]]
                main_value = str(weapon["statValue"])
                # 武器ステータス　文字追
                player_name = f"{main_name} : {main_value}"
                font_size = 25
                font_color = (255, 255, 255)
                height = 405 + cin*27
                width = 1100
                img = add_text_to_image(
                    img, player_name, font_size, font_color, height, width)

            # 武器名　文字追加
            player_name = genshinTextHash[n["flat"]["nameTextMapHash"]]
            font_size = 45
            font_color = (255, 255, 255)
            height = 370
            width = 1100
            img = add_text_to_image(
                img, player_name, font_size, font_color, height, width)

            try:
                # 凸、レベル　文字追加
                for z in n["weapon"]["affixMap"].values():
                    f = z
                player_name = f'精錬ランク{str(f+1)}  {n["weapon"]["level"]}Lv'
            except:
                player_name = f'{n["weapon"]["level"]}Lv'
            font_size = 28
            font_color = (255, 255, 255)
            height = 420
            width = 1100
            img = add_text_to_image(
                img, player_name, font_size, font_color, height, width)
        else:

            hogehoge += 1
            # 聖遺物の土台アイコン追加
            lank = n["flat"]["rankLevel"]
            icon = Image.open(
                f"Image/artifact/{str(lank)}.png").convert('RGBA').copy()
            icon = icon.resize(size=(260, 260), resample=Image.ANTIALIAS)
            base_img_clear = Image.new(
                "RGBA", base_img.size, (255, 255, 255, 0))
            # 円形用に合成
            #icon = mask_circle_transparent(icon, 2)
            icon = icon.rotate(random.randint(0, 360), resample=Image.BICUBIC)
            # バグ対策背景画像にアルファ合成
            base_img_clear.paste(icon, (1260, -170+hogehoge*132))
            # バグ対策できたんでちゃんと合成
            img = Image.alpha_composite(img, base_img_clear)

            # 聖遺物UI追加
            temp_3 = downloadPicture(
                f'https://enka.network/ui/{n["flat"]["icon"]}.png')
            icon = Image.open(temp_3).convert('RGBA').copy()
            icon = icon.resize(size=(76, 76), resample=Image.ANTIALIAS)
            base_img_clear = Image.new(
                "RGBA", base_img.size, (255, 255, 255, 0))
            # バグ対策背景画像にアルファ合成
            base_img_clear.paste(icon, (1350, -80+hogehoge*132))
            # バグ対策できたんでちゃんと合成
            img = Image.alpha_composite(img, base_img_clear)

            # メインステータス　文字追加
            mainValue = str(n["flat"]["reliquaryMainstat"]["statValue"])
            if "%" in mainValue or "会心" in mainValue or "チャ" in mainValue or "ダメージ" in mainValue:
                player_name = f'{mainValue}%'
            else:
                player_name = mainValue
            font_size = 40
            font_color = (255, 255, 255)
            height = -50+hogehoge*132
            width = 1450
            img = add_text_to_image(
                img, player_name, font_size, font_color, height, width)

            # メインステージ名　文字追加
            player_name = genshinTextHash[n["flat"]
                                          ["reliquaryMainstat"]["mainPropId"]]
            font_size = 20
            font_color = (255, 255, 255)
            height = -80+hogehoge*132
            width = 1450
            img = add_text_to_image(
                img, player_name, font_size, font_color, height, width)

            foo = 0
            for b in n["flat"]["reliquarySubstats"]:
                foo += 25
                # スコア値　文字追加
                mainValue = genshinTextHash[b["appendPropId"]]
                if "%" in mainValue or "会心" in mainValue or "チャ" in mainValue or "ダメージ" in mainValue:
                    player_name = f'{mainValue}：{b["statValue"]}%'
                else:
                    player_name = f'{mainValue}：{b["statValue"]}'
                font_size = 20
                font_color = (255, 255, 255)
                height = -110+hogehoge*132+foo
                width = 1650
                img = add_text_to_image(
                    img, player_name, font_size, font_color, height, width)
                statscore.append(
                    {genshinTextHash[b["appendPropId"]]: b["statValue"]})

            getscore = {genshinTextHash[n["flat"]["reliquaryMainstat"]
                                        ["mainPropId"]]: n["flat"]["reliquaryMainstat"]["statValue"]}
            # スコア値　文字追加
            player_name = f'+{n["reliquary"]["level"]-1}  スコア：{await genshinscore.score(statscore,getscore)}'
            font_size = 20
            font_color = (255, 255, 255)
            height = -5+hogehoge*132
            width = 1450
            img = add_text_to_image(
                img, player_name, font_size, font_color, height, width)

    await interaction.edit_original_message(content="```まもなく完了...```")
    filename = random.random()
    img.save(f'picture/{filename}.png')
    shutil.rmtree("temp")
    os.mkdir("temp")
    return f'picture/{filename}.png'
