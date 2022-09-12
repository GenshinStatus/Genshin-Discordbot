import discord
import aiohttp
from lib.yamlutil import yaml
import lib.scoreCalculator as genshinscore
from typing import List

charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinTextHash = genshinJpYaml.load_yaml()

async def get(uid,id):
    url = f"https://enka.network/u/{uid}/__data.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.json()
    name = characters[id]["NameId"]
    name = genshinTextHash[name]
    
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
