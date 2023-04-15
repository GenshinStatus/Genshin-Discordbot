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


def add_text_to_image(img, text, font_size, font_color, height, width, max_length=740, anchor=None, align=None):
    position = (width, height)
    font = ImageFont.truetype(
        font="./fonts/ja-jp.ttf", size=font_size)
    draw = ImageDraw.Draw(img)
    if draw.textsize(text, font=font)[0] > max_length:
        while draw.textsize(text + '…', font=font)[0] > max_length:
            text = text[:-1]
        text = text + '…'

    draw.text(position, text, font_color,
              font=font, anchor=anchor, align=align)
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
    # base_img.paste(icon, (80, 134), icon)

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
        base_img_clear.paste(icon, (36+x*35, 667))
    # バグ対策できたんでちゃんと合成
    base_img = Image.alpha_composite(base_img, base_img_clear)

    await interaction.edit_original_message(content="```キャラ基本情報取得中...```")
    # ユーザー名文字追加
    player_name = characterData.character.name
    font_size = 80
    font_color = (255, 255, 255)
    height = 564
    width = 34
    img = add_text_to_image(base_img, player_name,
                            font_size, font_color, height, width)

    # レベル文字追加
    player_name = f'{characterData.character.level}Lv  {characterData.character.constellations}凸'
    font_size = 24
    font_color = (255, 255, 255)
    height = 667
    width = 36+x*35+80
    img = add_text_to_image(base_img, player_name,
                            font_size, font_color, height, width)

    # HP基礎　文字追加
    player_name = characterData.character.base_hp
    font_size = 18
    font_color = (118, 255, 255)
    height = 92
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # HP聖遺物　文字追加
    player_name = f'+{characterData.character.added_hp}'
    font_size = 18
    font_color = (169, 255, 0)
    height = 92
    width = 383
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # HP合計値　文字追加
    player_name = str(int(characterData.character.base_hp) +
                      int(characterData.character.added_hp))
    font_size = 26
    font_color = (255, 255, 255)
    height = 62
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力基礎　文字追加
    player_name = characterData.character.base_attack
    font_size = 18
    font_color = (118, 255, 255)
    height = 158
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力聖遺物　文字追加
    player_name = f'+{characterData.character.added_attack}'
    font_size = 18
    font_color = (169, 255, 0)
    height = 158
    width = 383
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 攻撃力合計値　文字追加
    player_name = str(int(characterData.character.base_attack) +
                      int(characterData.character.added_attack))
    font_size = 26
    font_color = (255, 255, 255)
    height = 128
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力基礎　文字追加
    player_name = characterData.character.base_defense
    font_size = 18
    font_color = (118, 255, 255)
    height = 219
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力聖遺物　文字追加
    player_name = f'+{characterData.character.added_defense}'
    font_size = 18
    font_color = (169, 255, 0)
    height = 219
    width = 383
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 防御力合計値　文字追加
    player_name = str(int(characterData.character.base_defense) +
                      int(characterData.character.added_defense))
    font_size = 26
    font_color = (255, 255, 255)
    height = 189
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 会心率　文字追加
    player_name = f'{characterData.character.critical_rate}%'
    font_size = 26
    font_color = (255, 255, 255)
    height = 315
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 会心ダメ　文字追加
    player_name = f'{characterData.character.critical_damage}%'
    font_size = 26
    font_color = (255, 255, 255)
    height = 383
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 元素チャージ　文字追加
    player_name = f'{characterData.character.charge_efficiency}%'
    font_size = 26
    font_color = (255, 255, 255)
    height = 452
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 元素熟知　文字追加
    player_name = characterData.character.elemental_mastery
    font_size = 26
    font_color = (255, 255, 255)
    height = 252
    width = 313
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    if characterData.character.elemental_name != None:
        # 元素ダメバフ　文字追加
        player_name = characterData.character.elemental_name
        font_size = 20
        font_color = (277, 185, 128)
        height = 517
        width = 43
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

    if characterData.character.elemental_value != None:
        # 元素ダメバフ　文字追加
        player_name = characterData.character.elemental_value
        font_size = 26
        font_color = (255, 255, 255)
        height = 517
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
        icon = icon.resize(size=(100, 100), resample=Image.ANTIALIAS)
        base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
        # バグ対策背景画像にアルファ合成
        base_img_clear.paste(icon, (1025, -106+hogehoge*133))
        # バグ対策できたんでちゃんと合成
        img = Image.alpha_composite(img, base_img_clear)

    for level in characterData.character.skill_list_level:
        hogehoge += 1
        # 天賦　文字追加
        player_name = f"Lv.{level}"
        font_size = 50
        font_color = (255, 255, 255)
        height = -490+hogehoge*132
        width = 1155
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

    await interaction.edit_original_message(content="```キャラ聖遺物情報取得中...```")

    if characterData.weapon.name != None:
        # 武器アイコン追加
        temp_4 = downloadPicture(characterData.weapon.image)
        icon = Image.open(temp_4).convert('RGBA').copy()
        icon = icon.resize(size=(160, 160), resample=Image.ANTIALIAS)
        base_img_clear = Image.new(
            "RGBA", base_img.size, (255, 255, 255, 0))
        # バグ対策背景画像にアルファ合成
        base_img_clear.paste(icon, (720, 520))
        # バグ対策できたんでちゃんと合成
        img = Image.alpha_composite(img, base_img_clear)

        weapon_status = f"{characterData.weapon.main_name} : {characterData.weapon.main_value}"

        if characterData.weapon.sub_name != None:
            if "%" in characterData.weapon.sub_name or "会心" in characterData.weapon.sub_name or "チャ" in characterData.weapon.sub_name or "ダメージ" in characterData.weapon.sub_name:
                weapon_sub_value = f'{characterData.weapon.sub_value}%'
            else:
                weapon_sub_value = characterData.weapon.sub_value
            weapon_status = f"{weapon_status} // {characterData.weapon.sub_name} : {weapon_sub_value}"

        player_name = weapon_status
        font_size = 22
        font_color = (255, 255, 255)
        height = 632
        width = 1305
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width, anchor='rm', align='right')

        # 武器名　文字追加
        player_name = characterData.weapon.name
        # 文字数に応じて、文字サイズを計算
        char_width = 350 / len(characterData.weapon.name)
        font_size = min(int(char_width / 0.6), 60)  # 0.6は、文字の幅を表す係数
        font_color = (255, 255, 255)
        height = 545
        width = 1303
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width, anchor='ra', align='right')

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
        icon = icon.resize(size=(230, 230), resample=Image.ANTIALIAS)
        base_img_clear = Image.new(
            "RGBA", base_img.size, (255, 255, 255, 0))
        # 円形用に合成
        # icon = mask_circle_transparent(icon, 2)
        icon = icon.rotate(random.randint(0, 360), resample=Image.BICUBIC)
        # バグ対策背景画像にアルファ合成
        base_img_clear.paste(icon, (1275, -82+hogehoge*120))
        # バグ対策できたんでちゃんと合成
        img = Image.alpha_composite(img, base_img_clear)

        # 聖遺物UI追加
        temp_3 = downloadPicture(artifactData.image)
        icon = Image.open(temp_3).convert('RGBA').copy()
        icon = icon.resize(size=(76, 76), resample=Image.ANTIALIAS)
        base_img_clear = Image.new(
            "RGBA", base_img.size, (255, 255, 255, 0))
        # バグ対策背景画像にアルファ合成
        base_img_clear.paste(icon, (1352, -1+hogehoge*119))
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
        height = 33+hogehoge*120
        width = 1450
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)

        # メインステージ名　文字追加
        player_name = mainName
        font_size = 20
        font_color = (255, 255, 255)
        height = 3+hogehoge*120
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
            font_size = 15
            font_color = (255, 255, 255)
            height = -18+hogehoge*120+foo
            width = 1610
            if foo > 50:
                width = 1750
                height = -18+hogehoge*120+(foo-50)
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
