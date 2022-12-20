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


class CharacterStatus():
    def __init__(self, characterData, weaponData, artifactData):
        self.characterData = characterData
        self.weaponData = weaponData
        self.artifactData = artifactData

    async def getCharacterStatus(self, uid, id):
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
            raise FileNotFoundError

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
        for key, name in ELEMENT_DAMAGE_TYPES.items():
            if round(chara["fightPropMap"][key]*100) > 0:
                elemental_name = name
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
            name,
            image,
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
                        {genshinTextHash[b["appendPropId"]]: b["statValue"]})
                artifact_status_score = await genshinscore.score(artifact_status)
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


class character():
    def __init__(
        self,
        name: str,
        image: str,
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

        self.name = name
        self.image = image
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
    def __init__(self, main_name, main_value, ster, image, level, status: list, score):
        self.main_name = main_name
        self.main_value = main_value
        self.ster = ster
        self.image = image
        self.level = level
        self.status = status
        self.score = score


class weapon():
    def __init__(self, name, main_name, main_value, sub_name, sub_value, image, level, rank):
        self.name = name
        self.main_name = main_name
        self.main_value = main_value
        self.sub_name = sub_name
        self.sub_value = sub_value
        self.image = image
        self.level = level
        self.rank = rank
