from PIL import Image, ImageDraw, ImageFilter, ImageFont
import aiohttp
from lib.yamlutil import yaml
import requests
import urllib
import datetime
import os

dataYaml = yaml(path='genshin_avater.yaml')
data = dataYaml.load_yaml()
NameUtilYaml = yaml(path='characters.yaml')
NameUtil = NameUtilYaml.load_yaml()
characterNameYaml = yaml(path='genshinJp.yaml')
characterName = characterNameYaml.load_yaml()
genshinYaml = yaml('genshin.yaml')
genshinHYaml = yaml('genshinH.yaml')
words = genshinYaml.load_yaml()
jhwords = genshinHYaml.load_yaml()

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
    global jhwords
    hoge = []
    hoge.append(name)
    if name in ["コレイ","ティナリ"]:
        return words[name]["url"]
    if name in words:
        resalt = urllib.parse.quote(words[name]["zh"])
    elif name in jhwords:
        resalt = urllib.parse.quote(words[jhwords[name]["ja"]]["zh"])
    else:
        resalt = None
    return f"https://bbs.hoyolab.com/hoyowiki/picture/character/{resalt}/avatar.png"

async def getProfile(uid):
    url = f"https://enka.network/u/{uid}/__data.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.json()

    #プロフィールアイコン取得
    hoge = data[resp['playerInfo']['profilePicture']['avatarId']]['iconName']
    temp_1 = downloadPicture(f"https://enka.network/ui/{hoge}.png")
    icon = Image.open(temp_1).copy()
    #プロフィールアイコンのリサイズ
    icon = icon.resize(size=(160, 160), resample=Image.ANTIALIAS)
    #円形用マスクを作成
    mask = Image.new("L", icon.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, icon.size[0], icon.size[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1))
    #円形用に合成
    icon.putalpha(mask)

    #背景画像読み込み
    base_img = Image.open("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\AccountProfileBaseImage.png").convert('RGBA').copy()
    #バグ対策に背景を完全透過させたものを生成
    base_img_clear = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    #base_img.paste(icon, (80, 134), icon)

    #プロフィールアイコンキャラ絵の名前取得
    hoge = characterName[NameUtil[str(resp['playerInfo']['profilePicture']['avatarId'])]["NameId"]]
    #かえってきた名前から画像を取得（RGBA）
    temp_2 = downloadPicture(getCharacterPicture(hoge))
    character_Picture = Image.open(temp_2).copy()
    #画像の大きさを取得/3
    w, h = character_Picture.size
    w = w/3
    h = h/3
    #縮小
    character_Picture = character_Picture.resize(size=(round(w), round(h)), resample=Image.ANTIALIAS)
    #バグ対策背景画像にアルファ合成
    base_img_clear.paste(character_Picture)
    #バグ対策できたんでちゃんと合成
    base_img = Image.alpha_composite(base_img, base_img_clear)

    #手前の背景画像読み込み
    Secondbase_img = Image.open("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\AccountProfileImage.png").copy()
    #合成
    base_img.paste(Secondbase_img, (0, 120))

    #アイコン合成
    base_img.paste(icon, (0, 0), icon)

    #文字追加
    player_name = resp['playerInfo']['nickname']
    font_size = 40
    font_color = (255, 255, 255)
    height = 244
    width = 380
    img = add_text_to_image(base_img, player_name, font_size, font_color, height, width)

    img.save('C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\1.png')
    os.remove(temp_1)
    os.remove(temp_2)
    return "C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\1.png"