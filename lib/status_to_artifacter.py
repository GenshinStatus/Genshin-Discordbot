TEXTFIX = {
    "HP%": "HPパーセンテージ",
    "会心ダメ": "会心ダメージ",
    "元チャ効率": "元素チャージ効率",
    "元チャ": "元素チャージ効率",
    "攻撃力%": "攻撃パーセンテージ",
    "防御力%": "防御パーセンテージ"
}


def text_fix(input_text):
    return TEXTFIX.get(input_text, input_text)


def get_artifacter_data(uid, data):
    character = data.character
    weapon = data.weapon
    artifact = data.artifact

    total_score = 0
    for n in artifact:
        total_score += n.score

    sub = []
    temp = []
    for a in range(len(artifact)):
        for n in artifact[a].status:
            temp.append({"option": text_fix(n[0]), "value": float(n[1])})
        sub.append(temp)
        temp = []

    ELEMENT = {
        "Wind": "風",
        "Rock": "岩",
        "Electric": "雷",
        "Grass": "草",
        "Water": "水",
        "Fire": "炎",
        "Ice": "氷"
    }

    if character.constellations == "無":
        constellations = "0"
    elif character.constellations == "完":
        constellations = "6"
    else:
        constellations = character.constellations

    try:
        elemental_buff_name = str(text_fix(character.elemental_name))
        elemental_buff_value = float(
            character.elemental_value.replace('%', ''))
    except:
        elemental_buff_name = ""
        elemental_buff_value = ""

    result = {
        "uid": int(uid),
        "input": "",
        "Character": {
            "Name": str(character.name),
            "Const": int(constellations),
            "Level": int(character.level),
            "Love": int(character.love),
            "Status": {
                "HP": int(character.base_hp) + int(character.added_hp),
                "攻撃力": int(character.base_attack) + int(character.added_attack),
                "防御力": int(character.base_defense) + int(character.added_defense),
                "元素熟知": int(character.elemental_mastery),
                "会心率": float(character.critical_rate),
                "会心ダメージ": float(character.critical_damage),
                "元素チャージ効率": float(character.charge_efficiency),
                elemental_buff_name: elemental_buff_value
            },
            "Talent": {
                "通常": int(character.skill_list_level[0]),
                "スキル": int(character.skill_list_level[1]),
                "爆発": int(character.skill_list_level[2])
            },
            "Base": {
                "HP": int(character.base_hp),
                "攻撃力": int(character.base_attack),
                "防御力": int(character.base_defense),
            }
        },
        "Weapon": {
            "name": str(weapon.name),
            "Level": int(weapon.level),
            "totu": int(weapon.rank),
            "rarelity": 5,
            "BaseATK": int(weapon.main_value),
            "Sub": {
                "name": str(text_fix(weapon.sub_name)),
                "value": str(weapon.sub_value),
            }
        },
        "Score": {
            "State": text_fix(data.build_type.replace(" ver2", "")),
            "total": round(total_score, 1),
            "flower": artifact[0].score,
            "wing": artifact[1].score,
            "clock": artifact[2].score,
            "cup": artifact[3].score,
            "crown": artifact[4].score
        },
        "Artifacts": {
            "flower": {
                "type": str(artifact[0].artifact_set_name),
                "Level": int(artifact[0].level),
                "rarelity": int(artifact[0].ster),
                "main": {
                    "option": text_fix(artifact[0].main_name),
                    "value": int(artifact[0].main_value),
                },
                "sub": sub[0]
            },
            "wing": {
                "type": str(artifact[1].artifact_set_name),
                "Level": int(artifact[1].level),
                "rarelity": int(artifact[1].ster),
                "main": {
                    "option": text_fix(artifact[1].main_name),
                    "value": float(artifact[1].main_value),
                },
                "sub": sub[1]
            },
            "clock": {
                "type": str(artifact[2].artifact_set_name),
                "Level": int(artifact[2].level),
                "rarelity": int(artifact[2].ster),
                "main": {
                    "option": text_fix(artifact[2].main_name),
                    "value": float(artifact[2].main_value),
                },
                "sub": sub[2]
            },
            "cup": {
                "type": str(artifact[3].artifact_set_name),
                "Level": int(artifact[3].level),
                "rarelity": int(artifact[3].ster),
                "main": {
                    "option": text_fix(artifact[3].main_name),
                    "value": float(artifact[3].main_value),
                },
                "sub": sub[3]
            },
            "crown": {
                "type": str(artifact[4].artifact_set_name),
                "Level": int(artifact[4].level),
                "rarelity": int(artifact[4].ster),
                "main": {
                    "option": text_fix(artifact[4].main_name),
                    "value": float(artifact[4].main_value),
                },
                "sub": sub[4]
            },
        },
        "元素": ELEMENT[character.element]
    }

    return result