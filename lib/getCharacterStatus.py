from decimal import Decimal
import aiohttp
from lib.yamlutil import yaml
import lib.scoreCalculator as genshinscore
import urllib


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


charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinTextHash = genshinJpYaml.load_yaml()
wordsYaml = yaml(path='genshin.yaml')
words = wordsYaml.load_yaml()

ConfigYaml = yaml(path='genshinDataConfig.yaml')
config = ConfigYaml.load_yaml()


class character():
    def __init__(
        self,
        id,
        name: str,
        image: str,
        element: str,
        ster: int,
        constellations: str,
        level: str,
        base_hp: str,
        added_hp: str,
        base_attack: str,
        added_attack: str,
        base_defense: str,
        added_defense: str,
        critical_rate: str,
        critical_damage: str,
        charge_efficiency: str,
        elemental_mastery: str,
        elemental_name: str,
        elemental_value: str,
        skill_list_image: list,
        skill_list_level: list,
    ):

        self.id = id
        self.name = name
        self.image = image
        self.element = element
        self.ster = ster
        self.constellations = constellations
        self.level = level
        self.base_hp = base_hp
        self.added_hp = added_hp
        self.base_attack = base_attack
        self.added_attack = added_attack
        self.base_defense = base_defense
        self.added_defense = added_defense
        self.critical_rate = critical_rate
        self.critical_damage = critical_damage
        self.charge_efficiency = charge_efficiency
        self.elemental_mastery = elemental_mastery
        self.elemental_name = elemental_name
        self.elemental_value = elemental_value
        self.skill_list_image = skill_list_image
        self.skill_list_level = skill_list_level


class artifact():
    def __init__(
        self,
        main_name: str,
        main_value: str,
        ster: int,
        image: str,
        level: int,
        status: list[tuple[str, str]],
        score: Decimal,
    ):
        self.main_name = main_name
        self.main_value = main_value
        self.ster = ster
        self.image = image
        self.level = level
        self.status = status
        self.score = score


class weapon():
    def __init__(
        self,
        name: str,
        main_name: str,
        main_value: str,
        sub_name: str,
        sub_value: str,
        image: str,
        level: int,
        rank: int
    ):
        self.name = name
        self.main_name = main_name
        self.main_value = main_value
        self.sub_name = sub_name
        self.sub_value = sub_value
        self.image = image
        self.level = level
        self.rank = rank


class CharacterStatus():
    def __init__(self, characterData: character, weaponData: weapon, artifactData: list[artifact]):
        self.character = characterData
        self.weapon = weaponData
        self.artifact = artifactData

    def dict_to_character(id: int, resp: dict):
        name = genshinTextHash[characters[id]["NameId"]]
        image = getCharacterPicture(name)
        element = config[str(id)]['Element']
        ster = int(words[name]["ster"])
        try:
            # アバターインフォリストを回す。nにキャラ情報がすべて入る。
            # もしキャラクター情報が公開されていない、表示できない場合はFileNotFoundErrorでraiseする。
            for n in resp['avatarInfoList']:
                if n["avatarId"] == int(id):
                    chara = n
                    break
                else:
                    continue
        except:
            raise FileNotFoundError()

        # 凸情報。もし6凸、または0凸だった場合は、それに対応する日本語に変換する。
        try:
            constellations = str(len(chara["talentIdList"]))
            if constellations == "6":
                constellations = "完"
            elif constellations == "0":
                constellations = "無"
        except:
            constellations = "無"

        level = str(chara["propMap"]["4001"]["val"])
        base_hp = str(round(chara["fightPropMap"]["1"]))
        added_hp = str(
            round(chara["fightPropMap"]["2000"]) - round(chara["fightPropMap"]["1"]))
        base_attack = str(round(chara["fightPropMap"]["4"]))
        added_attack = str(
            round(chara["fightPropMap"]["2001"]) - round(chara["fightPropMap"]["4"]))
        base_defense = str(round(chara["fightPropMap"]["7"]))
        added_defense = str(
            round(chara["fightPropMap"]["2002"]) - round(chara["fightPropMap"]["7"]))

        critical_rate = str(round(chara["fightPropMap"]["20"] * 100))
        critical_damage = str(round(chara["fightPropMap"]["22"] * 100))
        charge_efficiency = str(round(chara["fightPropMap"]["23"] * 100))
        elemental_mastery = str(round(chara["fightPropMap"]["28"]))

        ELEMENT_DAMAGE_TYPES = {
            "30": "物理ダメージ",
            "40": "炎元素ダメージ",
            "41": "雷元素ダメージ",
            "42": "水元素ダメージ",
            "43": "草元素ダメージ",
            "44": "風元素ダメージ",
            "45": "岩元素ダメージ",
            "46": "氷元素ダメージ"
        }

        buf = 1
        fuga = None
        elemental_name = None
        elemental_value = None
        for key, fuga in ELEMENT_DAMAGE_TYPES.items():
            if round(chara["fightPropMap"][key]*100) > 0:
                elemental_name = fuga
                elemental_value = f'{str(round(chara["fightPropMap"][key]*100))}%'
                buf += round(chara["fightPropMap"][key])
                break

        skill_list_image = []
        for skill in config[id]['SkillOrder']:
            skill_list_image.append(
                f"https://enka.network/ui/{config[id]['Skills'][str(skill)]}.png")

        skill_list_level = [
            f"{myvalue}" for myvalue in chara["skillLevelMap"].values()]
        if len(chara["skillLevelMap"]) == 4:
            skill_list_level.pop(3)

        character_resalt = character(
            id,
            name,
            image,
            element,
            ster,
            constellations,
            level,
            base_hp,
            added_hp,
            base_attack,
            added_attack,
            base_defense,
            added_defense,
            critical_rate,
            critical_damage,
            charge_efficiency,
            elemental_mastery,
            elemental_name,
            elemental_value,
            skill_list_image,
            skill_list_level)

        artifact_resalt: list[artifact] = []
        weapon_image = None
        weapon_sub_name = None
        weapon_sub_value = None
        for n in chara["equipList"]:
            artifact_status = []
            if 'weapon' in n:
                # 武器アイコン追加
                weapon_image = f'https://enka.network/ui/{n["flat"]["icon"]}.png'

                hoge = 0
                for weaponData in n["flat"]["weaponStats"]:
                    hoge += 1
                    if hoge == 1:
                        weapon_main_name = genshinTextHash[weaponData["appendPropId"]]
                        weapon_main_value = str(weaponData["statValue"])
                    else:
                        weapon_sub_name = genshinTextHash[weaponData["appendPropId"]]
                        weapon_sub_value = str(weaponData["statValue"])

                weapon_name = genshinTextHash[n["flat"]["nameTextMapHash"]]

                weapon_rank = None
                try:
                    for z in n["weapon"]["affixMap"].values():
                        f = z
                    weapon_level = n["weapon"]["level"]
                    weapon_rank = str(f+1)
                except:
                    weapon_level = n["weapon"]["level"]

                weapon_resalt = weapon(
                    weapon_name,
                    weapon_main_name,
                    weapon_main_value,
                    weapon_sub_name,
                    weapon_sub_value,
                    weapon_image,
                    weapon_level,
                    weapon_rank)

            else:

                artifact_ster = n["flat"]["rankLevel"]
                artifact_image = f'https://enka.network/ui/{n["flat"]["icon"]}.png'
                artifact_main_name = genshinTextHash[n["flat"]
                                                     ["reliquaryMainstat"]["mainPropId"]]
                artifact_main_value = str(
                    n["flat"]["reliquaryMainstat"]["statValue"])
                for b in n["flat"]["reliquarySubstats"]:
                    artifact_status.append(
                        (
                            genshinTextHash[b["appendPropId"]],
                            b["statValue"],
                        )
                    )

                def score(dict):
                    resalt = 0
                    attack = 0
                    critical = 0
                    critical_hurt = 0
                    # 4つのステータス分回す
                    for n in dict:
                        k = n[0]
                        v = n[1]
                        # とりあえず関連するステータスかどうかのfor
                        if k == "攻撃力%":
                            attack = str(v)
                        elif k == "会心率":
                            critical = str(v)
                        elif k == "会心ダメージ":
                            critical_hurt = str(v)
                    # forが終わったら計算
                    hoge = Decimal(critical)*2
                    resalt = Decimal(attack) + Decimal(hoge) + \
                        Decimal(critical_hurt)
                    return resalt

                artifact_status_score = score(artifact_status)
                aritifact_level = n["reliquary"]["level"]-1

                artifact_resalt.append(
                    artifact(
                        artifact_main_name,
                        artifact_main_value,
                        artifact_ster,
                        artifact_image,
                        aritifact_level,
                        artifact_status,
                        artifact_status_score,
                    ))

        return CharacterStatus(character_resalt, weapon_resalt, artifact_resalt)

    async def getCharacterStatus(uid, id):
        """
        uidからキャラクター情報を読み取ります。
        《self.character》
        ・name キャラクター名

        """
        url = f"https://enka.network/u/{uid}/__data.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.json()
        name = genshinTextHash[characters[id]["NameId"]]
        image = getCharacterPicture(name)
        element = config[str(id)]['Element']
        ster = int(words[name]["ster"])
        try:
            # アバターインフォリストを回す。nにキャラ情報がすべて入る。
            # もしキャラクター情報が公開されていない、表示できない場合はFileNotFoundErrorでraiseする。
            for n in resp['avatarInfoList']:
                if n["avatarId"] == int(id):
                    chara = n
                    break
                else:
                    continue
        except:
            raise FileNotFoundError()

            # 凸情報。もし6凸、または0凸だった場合は、それに対応する日本語に変換する。
        try:
            constellations = str(len(chara["talentIdList"]))
            if constellations == "6":
                constellations = "完"
            elif constellations == "0":
                constellations = "無"
        except:
            constellations = "無"

        level = str(chara["propMap"]["4001"]["val"])
        base_hp = str(round(chara["fightPropMap"]["1"]))
        added_hp = str(
            round(chara["fightPropMap"]["2000"]) - round(chara["fightPropMap"]["1"]))
        base_attack = str(round(chara["fightPropMap"]["4"]))
        added_attack = str(
            round(chara["fightPropMap"]["2001"]) - round(chara["fightPropMap"]["4"]))
        base_defense = str(round(chara["fightPropMap"]["7"]))
        added_defense = str(
            round(chara["fightPropMap"]["2002"]) - round(chara["fightPropMap"]["7"]))

        critical_rate = str(round(chara["fightPropMap"]["20"] * 100))
        critical_damage = str(round(chara["fightPropMap"]["22"] * 100))
        charge_efficiency = str(round(chara["fightPropMap"]["23"] * 100))
        elemental_mastery = str(round(chara["fightPropMap"]["28"]))

        ELEMENT_DAMAGE_TYPES = {
            "30": "物理ダメージ",
            "40": "炎元素ダメージ",
            "41": "雷元素ダメージ",
            "42": "水元素ダメージ",
            "43": "草元素ダメージ",
            "44": "風元素ダメージ",
            "45": "岩元素ダメージ",
            "46": "氷元素ダメージ"
        }

        buf = 1
        fuga = None
        elemental_name = None
        elemental_value = None
        for key, fuga in ELEMENT_DAMAGE_TYPES.items():
            if round(chara["fightPropMap"][key]*100) > 0:
                elemental_name = fuga
                elemental_value = f'{str(round(chara["fightPropMap"][key]*100))}%'
                buf += round(chara["fightPropMap"][key])
                break

        skill_list_image = []
        for skill in config[id]['SkillOrder']:
            skill_list_image.append(
                f"https://enka.network/ui/{config[id]['Skills'][str(skill)]}.png")

        skill_list_level = [
            f"{myvalue}" for myvalue in chara["skillLevelMap"].values()]
        if len(chara["skillLevelMap"]) == 4:
            skill_list_level.pop(3)

        character_resalt = character(
            id,
            name,
            image,
            element,
            ster,
            constellations,
            level,
            base_hp,
            added_hp,
            base_attack,
            added_attack,
            base_defense,
            added_defense,
            critical_rate,
            critical_damage,
            charge_efficiency,
            elemental_mastery,
            elemental_name,
            elemental_value,
            skill_list_image,
            skill_list_level)

        artifact_resalt: list[artifact] = []
        weapon_image = None
        weapon_sub_name = None
        weapon_sub_value = None
        for n in chara["equipList"]:
            artifact_status = []
            if 'weapon' in n:
                # 武器アイコン追加
                weapon_image = f'https://enka.network/ui/{n["flat"]["icon"]}.png'

                hoge = 0
                for weaponData in n["flat"]["weaponStats"]:
                    hoge += 1
                    if hoge == 1:
                        weapon_main_name = genshinTextHash[weaponData["appendPropId"]]
                        weapon_main_value = str(weaponData["statValue"])
                    else:
                        weapon_sub_name = genshinTextHash[weaponData["appendPropId"]]
                        weapon_sub_value = str(weaponData["statValue"])

                weapon_name = genshinTextHash[n["flat"]["nameTextMapHash"]]

                weapon_rank = None
                try:
                    for z in n["weapon"]["affixMap"].values():
                        f = z
                    weapon_level = n["weapon"]["level"]
                    weapon_rank = str(f+1)
                except:
                    weapon_level = n["weapon"]["level"]

                weapon_resalt = weapon(
                    weapon_name,
                    weapon_main_name,
                    weapon_main_value,
                    weapon_sub_name,
                    weapon_sub_value,
                    weapon_image,
                    weapon_level,
                    weapon_rank)

            else:

                artifact_ster = n["flat"]["rankLevel"]
                artifact_image = f'https://enka.network/ui/{n["flat"]["icon"]}.png'
                artifact_main_name = genshinTextHash[n["flat"]
                                                     ["reliquaryMainstat"]["mainPropId"]]
                artifact_main_value = str(
                    n["flat"]["reliquaryMainstat"]["statValue"])
                for b in n["flat"]["reliquarySubstats"]:
                    artifact_status.append(
                        (genshinTextHash[b["appendPropId"]], b["statValue"]))
                artifact_status_score = genshinscore.score(artifact_status)
                aritifact_level = n["reliquary"]["level"]-1

                artifact_resalt.append(
                    artifact(
                        artifact_main_name,
                        artifact_main_value,
                        artifact_ster,
                        artifact_image,
                        aritifact_level,
                        artifact_status,
                        artifact_status_score,
                    ))

        return CharacterStatus(character_resalt, weapon_resalt, artifact_resalt)
