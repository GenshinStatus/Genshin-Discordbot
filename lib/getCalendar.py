from PIL import Image, ImageDraw, ImageFilter, ImageFont
import aiohttp
from lib.yamlutil import yaml
import requests
import urllib
import datetime
import os
import google.calendar as calendar

calendar.get()


def add_text_to_image(img, text, font_size, font_color, height, width, max_length=740):
    position = (width, height)
    font = ImageFont.truetype(
        font="C:\\Users\\Cinnamon\\AppData\\Local\\Microsoft\\Windows\\Fonts\\ja-jp.ttf", size=font_size)
    draw = ImageDraw.Draw(img)
    if draw.textsize(text, font=font)[0] > max_length:
        while draw.textsize(text + '…', font=font)[0] > max_length:
            text = text[:-1]
        text = text + '…'

    draw.text(position, text, font_color, font=font)
    return img


def getCharacterPicture(name):
    global words
    global jhwords
    hoge = []
    hoge.append(name)
    if name in ["コレイ", "ティナリ", "旅人", "ニィロウ", "キャンディス", "セノ", "ナヒーダ", "レイラ"]:
        return words[name]["url"]
    if name in words:
        resalt = urllib.parse.quote(words[name]["zh"])
    elif name in jhwords:
        resalt = urllib.parse.quote(words[jhwords[name]["ja"]]["zh"])
    else:
        resalt = None
    return f"https://bbs.hoyolab.com/hoyowiki/picture/character/{resalt}/avatar.png"


async def getProfile(uid, resp):
    # 背景画像読み込み
    base_img = Image.open(
        "C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\ProfileImage.png").convert('RGBA').copy()

    # ユーザー名文字追加
    player_name = resp['playerInfo']['nickname']
    font_size = 45
    font_color = (255, 255, 255)
    height = 125
    width = 260
    img = add_text_to_image(base_img, player_name,
                            font_size, font_color, height, width)

    # ステータスメッセージ文字追加
    try:
        player_name = resp['playerInfo']['signature']
        font_size = 18
        font_color = (255, 255, 255)
        height = 180
        width = 260
        img = add_text_to_image(
            img, player_name, font_size, font_color, height, width)
    except:
        print("すてーたすめっせーじだよ")

    # UID文字追加
    player_name = f"UID:{uid}"
    font_size = 18
    font_color = (255, 255, 255)
    height = 80
    width = 565
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # レベル文字追加
    player_name = str(resp['playerInfo']['level'])
    font_size = 45
    font_color = (255, 255, 255)
    height = 255
    width = 50
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 世界レベル文字追加
    player_name = str(resp['playerInfo']['worldLevel'])
    font_size = 45
    font_color = (255, 255, 255)
    height = 335
    width = 50
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # 螺旋文字追加
    player_name = f"{resp['playerInfo']['towerFloorIndex']}-{resp['playerInfo']['towerLevelIndex']}"
    font_size = 45
    font_color = (255, 255, 255)
    height = 255
    width = 295
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # アチーブメント文字追加
    player_name = f"{resp['playerInfo']['finishAchievementNum']}"
    font_size = 45
    font_color = (255, 255, 255)
    height = 335
    width = 295
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    # クレジット文字追加
    player_name = f"原神ステータスbot"
    font_size = 12
    font_color = (255, 255, 255)
    height = 380
    width = 600
    img = add_text_to_image(img, player_name, font_size,
                            font_color, height, width)

    img.save('C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\2.png')
    return "C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\2.png"
