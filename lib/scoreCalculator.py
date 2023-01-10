from decimal import Decimal


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
        elif k == "会心ダメ":
            critical_hurt = str(v)
    # forが終わったら計算
    hoge = Decimal(critical)*2
    resalt = Decimal(attack) + Decimal(hoge) + \
        Decimal(critical_hurt)
    return resalt
