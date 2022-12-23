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
from lib.GImage import GImage, Colors, Algin, Anchors, ImageAnchors


def downloadPicture(url):
    now = datetime.datetime.now()
    time_now = "{0:%Y%m%d_%H%M-%S_%f}".format(now)
    file_name = f"{time_now}.png"
    response = requests.get(url)
    image = response.content

    with open(f"temp/{file_name}", "wb") as aaa:
        aaa.write(image)
    return f"temp/{file_name}"


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
        # ここはキャラ詳細が非公開な旨を記述した画像を返す予定

    await interaction.edit_original_message(content="```準備中...```")
    # 読み込み準備中
    base_img = GImage(
        image_path=f"Image/status_bata/{characterData.character.element}.png",
        default_font_path="C:\\Users\\Cinnamon\\AppData\\Local\\Microsoft\\Windows\\Fonts\\ja-jp.ttf",
        default_font_size=26,
        default_font_color=Colors.WHITE
    )

    # キャラ画像合成
    base_img.add_image(
        image_path=downloadPicture(characterData.character.image),
        box=(660, 360),
        size=(1200, 820),
        image_anchor=ImageAnchors.MIDDLE_MIDDLE
    )

    # テキスト画像でサンドイッチ
    base_img.add_image(
        image_path="Image/status_bata/base.png",
        box=(0, 0),
    )

    # 星の数だけ合成
    for x in range(characterData.character.ster):
        base_img.add_image(
            image_path="Image/ster.png",
            box=(36+x*35, 667),
        )

    await interaction.edit_original_message(content="```キャラ基本情報取得中...```")

    # ユーザー名文字追加
    base_img.draw_text(
        text=characterData.character.name,
        position=(34, 564),
        font_size=80
    )

    # レベル文字追加
    base_img.draw_text(
        text=f'{characterData.character.level}Lv  {characterData.character.constellations}凸',
        position=(36+x*35+80, 667),
        font_size=24
    )

    # HP基礎　文字追加
    base_img.draw_text(
        text=characterData.character.base_hp,
        position=(313, 92),
        font_size=18,
        font_color=Colors.CYAN
    )

    # HP聖遺物　文字追加
    base_img.draw_text(
        text=f'+{characterData.character.added_hp}',
        position=(383, 92),
        font_size=18,
        font_color=Colors.GREEN
    )

    # HP合計値　文字追加
    base_img.draw_text(
        text=str(int(characterData.character.base_hp) +
                 int(characterData.character.added_hp)),
        position=(313, 62),
    )

    # 攻撃力基礎　文字追加
    base_img.draw_text(
        text=characterData.character.base_attack,
        position=(313, 158),
        font_size=18,
        font_color=Colors.CYAN
    )

    # 攻撃力聖遺物　文字追加
    base_img.draw_text(
        text=f'+{characterData.character.added_attack}',
        position=(383, 158),
        font_size=18,
        font_color=Colors.GREEN
    )

    # 攻撃力合計値　文字追加
    base_img.draw_text(
        text=str(int(characterData.character.base_attack) +
                 int(characterData.character.added_attack)),
        position=(313, 128),
    )

    # 防御力基礎　文字追加
    base_img.draw_text(
        text=characterData.character.base_defense,
        position=(313, 219),
        font_size=18,
        font_color=Colors.CYAN
    )

    # 防御力聖遺物　文字追加
    base_img.draw_text(
        text=f'+{characterData.character.added_defense}',
        position=(383, 219),
        font_size=18,
        font_color=Colors.GREEN
    )

    # 防御力合計値　文字追加
    base_img.draw_text(
        text=str(int(characterData.character.base_defense) +
                 int(characterData.character.added_defense)),
        position=(313, 189),
    )

    # 会心率　文字追加
    base_img.draw_text(
        text=f'{characterData.character.critical_rate}%',
        position=(313, 315),
    )

    # 会心ダメ　文字追加
    base_img.draw_text(
        text=f'{characterData.character.critical_damage}%',
        position=(313, 383),
    )

    # 元素チャージ　文字追加
    base_img.draw_text(
        text=f'{characterData.character.charge_efficiency}%',
        position=(313, 452),
    )

    # 元素熟知　文字追加
    base_img.draw_text(
        text=characterData.character.elemental_mastery,
        position=(313, 252),
    )

    if characterData.character.elemental_name != None:
        # 元素ダメバフ　文字追加
        base_img.draw_text(
            text=characterData.character.elemental_name,
            position=(43, 517),
            font_size=20
        )

    if characterData.character.elemental_value != None:
        # 元素ダメバフ　文字追加
        base_img.draw_text(
            text=characterData.character.elemental_value,
            position=(220, 517),
        )

    await interaction.edit_original_message(content="```キャラ天賦情報取得中...```")
    hogehoge = 0
    for skill in characterData.character.skill_list_image:
        hogehoge += 1
        temp_2 = downloadPicture(skill)
        # 天賦アイコン追加
        base_img.add_image(
            image_path=temp_2,
            box=(1025, -106+hogehoge*133),
            size=(100, 100),
        )

    for level in characterData.character.skill_list_level:
        hogehoge += 1
        # 天賦　文字追加
        base_img.draw_text(
            text=f"Lv.{level}",
            position=(1155, -490+hogehoge*132),
            font_size=50,
        )

    await interaction.edit_original_message(content="```キャラ聖遺物情報取得中...```")

    if characterData.weapon.name != None:
        # 武器アイコン追加
        temp_4 = downloadPicture(characterData.weapon.image)
        base_img.add_image(
            image_path=temp_4,
            box=(720, 520),
            size=(160, 160),
        )

        weapon_status = f"{characterData.weapon.main_name} : {characterData.weapon.main_value}"

        if characterData.weapon.sub_name != None:
            if "%" in characterData.weapon.sub_name or "会心" in characterData.weapon.sub_name or "チャ" in characterData.weapon.sub_name or "ダメージ" in characterData.weapon.sub_name:
                weapon_sub_value = f'{characterData.weapon.sub_value}%'
            else:
                weapon_sub_value = characterData.weapon.sub_value
            weapon_status = f"{weapon_status} // {characterData.weapon.sub_name} : {weapon_sub_value}"

        base_img.draw_text(
            text=weapon_status,
            position=(1305, 632),
            font_size=22,
            anchor='rm',
            align='right'
        )

        # 武器名　文字追加
        # 文字数に応じて、文字サイズを計算
        char_width = 350 / len(characterData.weapon.name)
        font_size = min(int(char_width / 0.6), 60)  # 0.6は、文字の幅を表す係数
        base_img.draw_text(
            text=characterData.weapon.name,
            position=(1303, 545),
            font_size=font_size,
            anchor='ra',
            align='right'
        )

        if characterData.weapon.rank != None:
            # 凸、レベル　文字追加
            player_name = f'精錬ランク{characterData.weapon.rank}  {characterData.weapon.level}Lv'
        else:
            player_name = f'{characterData.weapon.level}Lv'
        base_img.draw_text(
            text=player_name,
            position=(1100, 420),
            font_size=28,
        )

    hogehoge = 0
    for artifactData in characterData.artifact:
        hogehoge += 1
        # 聖遺物の土台アイコン追加

        icon = Image.open(
            f"Image/artifact/{artifactData.ster}.png").convert('RGBA').copy()
        icon = icon.resize(size=(230, 230), resample=Image.ANTIALIAS)
        icon = icon.rotate(random.randint(0, 360), resample=Image.BICUBIC)
        base_img.add_image_object(
            im=icon,
            box=(1275, -82+hogehoge*120),
        )

        # 聖遺物UI追加
        temp_3 = downloadPicture(artifactData.image)
        base_img.add_image(
            image_path=temp_3,
            box=(1352, -1+hogehoge*119),
            size=(76, 76),
        )

        # メインステータス　文字追加
        mainName = artifactData.main_name
        mainValue = artifactData.main_value
        if "%" in mainName or "会心" in mainName or "チャ" in mainName or "ダメージ" in mainName:
            player_name = f'{mainValue}%'
        else:
            player_name = mainValue
        base_img.draw_text(
            text=player_name,
            position=(1450, 33+hogehoge*120),
            font_size=40,
        )

        # メインステージ名　文字追加
        base_img.draw_text(
            text=mainName,
            position=(1450, 3+hogehoge*120),
            font_size=20,
        )

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
            if foo > 50:
                width = 1750
                height = -18+hogehoge*120+(foo-50)
            else:
                height = -18+hogehoge*120+foo
                width = 1610
            base_img.draw_text(
                text=player_name,
                position=(width, height),
                font_size=15,
            )

        # スコア値　文字追加
        base_img.draw_text(
            text=f'+{artifactData.level}  スコア：{artifactData.score}',
            position=(1450, -5+hogehoge*132),
            font_size=20,
        )

    await interaction.edit_original_message(content="```まもなく完了...```")
    filename = random.random()
    base_img.save(f'picture/{filename}.png')
    shutil.rmtree("temp")
    os.mkdir("temp")
    return f'picture/{filename}.png'
