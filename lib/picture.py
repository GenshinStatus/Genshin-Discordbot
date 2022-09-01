from PIL import Image, ImageDraw, ImageFilter, ImageFont
import aiohttp
from lib.yamlutil import yaml

def add_text_to_image(img, text, font_size, font_color, height, width, max_length=740):
    position = (width, height)
    font = ImageFont.truetype(font="C:\\Users\\Cinnamon\\AppData\\Local\\Microsoft\\Windows\\Fonts",size=font_size)
    draw = ImageDraw.Draw(img)
    if draw.textsize(text, font=font)[0] > max_length:
        while draw.textsize(text + '…', font=font)[0] > max_length:
            text = text[:-1]
        text = text + '…'

    draw.text(position, text, font_color, font=font)

    return img

dataYaml = yaml(path='genshin_avater.yaml')
data = dataYaml.load_yaml()

async def getProfile(uid):
    url = f"https://enka.network/u/{uid}/__data.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.json()

    #プロフィールアイコン取得
    hoge = data[resp['playerInfo']['profilePicture']['avatarId']]['iconName']
    icon_path = f"https://enka.network/ui/{hoge}.png"
    icon = Image.open(icon_path).copy()
    #プロフィールアイコンのリサイズ
    icon = icon.resize(size=(252, 252), resample=Image.ANTIALIAS)
    #円形用マスクを作成
    mask = Image.new("L", icon.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, icon.size[0], icon.size[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1))
    #円形用に合成
    icon.putalpha(mask)

    #背景画像読み込み
    base_image_path = 'https://zoomasobi.com/wp-content/uploads/2020/03/0f4c81_ClassicBlue.png'
    base_img = Image.open(base_image_path).copy()
    base_img.paste(icon, (80, 134), icon)

    #文字追加
    player_name = resp['playerInfo']['nickname']
    font_size = 40
    font_color = (255, 255, 255)
    height = 244
    width = 380
    img = add_text_to_image(base_img, player_name, font_size, font_color, height, width)

    img.save('C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\1')
    return "C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\picture\\1"