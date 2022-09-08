import discord
import aiohttp
from lib.yamlutil import yaml
import lib.scoreCalculator as genshinscore
from typing import List

charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinJp = genshinJpYaml.load_yaml()

async def get(uid,id):
    url = f"https://enka.network/u/{uid}/__data.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.json()
    name = characters[id]["NameId"]
    name = genshinJp[name]
    print(id)
    id = int(id)
    try:
        for n in resp['avatarInfoList']:
            if n["avatarId"] == id:
                chara = n
                print("hogehogheogheohgpoihvgp;ogiazwqp;oabwo")
                break
            else:
                continue
        for n in resp['playerInfo']["showAvatarInfoList"]:
            print(n["avatarId"])
            if n["avatarId"] == id:
                level = n["level"]
                print("hogehogehoge")
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
        embed = discord.Embed( 
                    title=name,
                    color=0x1e90ff, 
                    description=f"{level}lv", 
                    url=url 
                    )
        hoge = characters[str(id)]["sideIconName"]
        embed.set_thumbnail(url=f"https://enka.network/ui/{hoge}.png")
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
        for n in chara["equipList"]:
            name = genshinJp[n["flat"]["setNameTextMapHash"]]
            equip = genshinJp[n["flat"]["equipType"]]
            main = genshinJp[n["flat"]["reliquaryMainstat"]["mainPropId"]]
            hoge = []
            statscore = []
            for b in n["flat"]["reliquarySubstats"]:
                name_ = genshinJp[b["appendPropId"]]
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
        return embed
