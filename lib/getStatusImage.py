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
import lib.getCharacterStatus as getCharacterData


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
    try:
        characterData: getCharacterData.CharacterStatus = await getCharacterData.CharacterStatus.getCharacterStatus(uid=uid, id=id)
    except FileNotFoundError:
        embed = discord.Embed(
            title="エラー",
            color=0x1e90ff,
            description=f"キャラ詳細が非公開です。原神の設定で公開設定にしてください。",
        )
        return embed

    # プロフィールアイコン取得
    temp_1 = downloadPicture(characterData.character.image)
    icon = Image.open(temp_1).convert('RGBA').copy()
    # プロフィールアイコンのリサイズ
    s = 720/icon.height
    icon = icon.resize(size=(round(icon.width*s)+100,
                       round(icon.height*s)+100), resample=Image.ANTIALIAS)

    await interaction.edit_original_message(content="```準備中...```")
    # 背景画像読み込み
    base_img = Image.open(
        f"Image/status_bata/{characterData.character.element}.png").convert('RGBA').copy()
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
    icon = Image.open("Image/status_bata/base.png").convert('RGBA').copy()
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
    for x in range(characterData.character.ster):
        base_img_clear.paste(icon, (50+x*40, 130))
    # バグ対策できたんでちゃんと合成
    base_img = Image.alpha_composite(base_img, base_img_clear)

    await interaction.edit_original_message(content="```キャラ基本情報取得中...```")
    # ユーザー名文字追加
    player_name = characterData.character.name
    font_size = 88
    font_color = (255, 255, 255)
    height = 23
    width = 56
    img = add_text_to_image(base_img, player_name,
                            font_size, font_color, height, width)

    # レベル文字追加
    player_name = f'{characterData.character.level}Lv  {characterData.character.constellations}凸'
    font_size = 24
    font_color = (255, 255, 255)
    height = 130
    width = 50+x*40+40
    img = add_text_to_image(base_img, player_name,
                            font_size, font_color, height, width)

    # HP基礎　文字追加
    player_name = characterData.character.base_hp
    font_size = 20
    font_color = (255, 255, 255)
    height = 211
    width = 200
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # HP聖遺物　文字追加
    player_name = f'+{characterData.character.added_hp}'
    font_size = 20
    font_color = (169, 255, 0)
    height = 211
    width = 270
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # HP合計値　文字追加
    player_name = str(int(characterData.character.base_hp) +
                      int(characterData.character.added_hp))
    font_size = 32
    font_color = (118, 255, 255)
    height = 175
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力基礎　文字追加
    player_name = characterData.character.base_attack
    font_size = 20
    font_color = (255, 255, 255)
    height = 278
    width = 200
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力聖遺物　文字追加
    player_name = f'+{characterData.character.added_attack}'
    font_size = 20
    font_color = (169, 255, 0)
    height = 278
    width = 270
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力合計値　文字追加
    player_name = str(int(characterData.character.base_attack) +
                      int(characterData.character.added_attack))
    font_size = 32
    font_color = (118, 255, 255)
    height = 241
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力基礎　文字追加
    player_name = characterData.character.base_defense
    font_size = 20
    font_color = (255, 255, 255)
    height = 345
    width = 200
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力聖遺物　文字追加
    player_name = f'+{characterData.character.added_defense}'
    font_size = 20
    font_color = (169, 255, 0)
    height = 345
    width = 270
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力合計値　文字追加
    player_name = str(int(characterData.character.base_defense) +
                      int(characterData.character.added_defense))
    font_size = 32
    font_color = (118, 255, 255)
    height = 307
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 会心率　文字追加
    player_name = f'{characterData.character.critical_rate}%'
    font_size = 32
    font_color = (118, 255, 255)
    height = 386
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 会心ダメ　文字追加
    player_name = f'{characterData.character.critical_damage}%'
    font_size = 32
    font_color = (118, 255, 255)
    height = 446
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 元素チャージ　文字追加
    player_name = f'{characterData.character.charge_efficiency}%'
    font_size = 32
    font_color = (118, 255, 255)
    height = 518
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 元素熟知　文字追加
    player_name = characterData.character.elemental_mastery
    font_size = 32
    font_color = (118, 255, 255)
    height = 583
    width = 220
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    if characterData.character.elemental_name != None:
        # 元素ダメバフ　文字追加
        player_name = characterData.character.elemental_name
        font_size = 22
        font_color = (277, 185, 128)
        height = 655
        width = 38
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

    if characterData.character.elemental_value != None:
        # 元素ダメバフ　文字追加
        player_name = characterData.character.elemental_value
        font_size = 32
        font_color = (118, 255, 255)
        height = 650
        width = 220
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

    await interaction.edit_original_message(content="```キャラ天賦情報取得中...```")
    hogehoge = 0
    for skill in characterData.character.skill_list_image:
        hogehoge += 1
        # 天賦アイコン追加
        temp_2 = downloadPicture(skill)
        icon = Image.open(temp_2).convert('RGBA').copy()
        icon = icon.resize(size=(96, 96), resample=Image.ANTIALIAS)
        base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
        # バグ対策背景画像にアルファ合成
        base_img_clear.paste(icon, (1100, -50+hogehoge*101))
        # バグ対策できたんでちゃんと合成
        img = Image.alpha_composite(img, base_img_clear)

    for level in characterData.character.skill_list_level:
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

    if characterData.weapon.name != None:
        # 武器アイコン追加
        temp_4 = downloadPicture(characterData.weapon.image)
        icon = Image.open(temp_4).convert('RGBA').copy()
        icon = icon.resize(size=(225, 225), resample=Image.ANTIALIAS)
        base_img_clear = Image.new(
            "RGBA", base_img.size, (255, 255, 255, 0))
        # バグ対策背景画像にアルファ合成
        base_img_clear.paste(icon, (1100, 505))
        # バグ対策できたんでちゃんと合成
        img = Image.alpha_composite(img, base_img_clear)

        player_name = f"{characterData.weapon.main_name} : {characterData.weapon.main_value}"
        font_size = 25
        font_color = (255, 255, 255)
        height = 405 + 1*27
        width = 1100
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

        if characterData.weapon.sub_name != None:
            player_name = f"{characterData.weapon.sub_name} : {characterData.weapon.sub_value}"
            font_size = 25
            font_color = (255, 255, 255)
            height = 405 + 2*27
            width = 1100
            img = add_text_to_image(
                img, player_name, font_size, font_color, height, width)

        # 武器名　文字追加
        player_name = characterData.weapon.name
        font_size = 45
        font_color = (255, 255, 255)
        height = 370
        width = 1100
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

        if characterData.weapon.rank != None:
            # 凸、レベル　文字追加
            player_name = f'精錬ランク{characterData.weapon.rank}  {characterData.weapon.level}Lv'
        else:
            player_name = f'{characterData.weapon.level}Lv'
        font_size = 28
        font_color = (255, 255, 255)
        height = 420
        width = 1100
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

    hogehoge = 0
    for artifactData in characterData.artifact:
        hoge = []
        statscore = []
        hogehoge += 1
        # 聖遺物の土台アイコン追加
        icon = Image.open(
            f"Image/artifact/{artifactData.ster}.png").convert('RGBA').copy()
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
        temp_3 = downloadPicture(artifactData.image)
        icon = Image.open(temp_3).convert('RGBA').copy()
        icon = icon.resize(size=(76, 76), resample=Image.ANTIALIAS)
        base_img_clear = Image.new(
            "RGBA", base_img.size, (255, 255, 255, 0))
        # バグ対策背景画像にアルファ合成
        base_img_clear.paste(icon, (1350, -80+hogehoge*132))
        # バグ対策できたんでちゃんと合成
        img = Image.alpha_composite(img, base_img_clear)

        # メインステータス　文字追加
        mainName = artifactData.main_name
        mainValue = artifactData.main_value
        if "%" in mainName or "会心" in mainName or "チャ" in mainName or "ダメージ" in mainName:
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
        player_name = mainName
        font_size = 20
        font_color = (255, 255, 255)
        height = -80+hogehoge*132
        width = 1450
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

        foo = 0
        for n in artifactData.status:
            for k, v in n.items():
                mainValue = k
            foo += 25
            # スコア値　文字追加
            if "%" in mainValue or "会心" in mainValue or "チャ" in mainValue or "ダメージ" in mainValue:
                player_name = f'{mainValue}：{v}%'
            else:
                player_name = f'{mainValue}：{v}'
            font_size = 20
            font_color = (255, 255, 255)
            height = -110+hogehoge*132+foo
            width = 1650
            img = add_text_to_image(
                img, player_name, font_size, font_color, height, width)

        # スコア値　文字追加
        player_name = f'+{artifactData.level}  スコア：{artifactData.score}'
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
