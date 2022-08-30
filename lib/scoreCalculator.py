from decimal import Decimal

async def score(dict,main):
    resalt = 0
    attack = 0
    critical = 0
    critical_hurt = 0
    #for k,v in main.items():
        #if k == "攻撃力%":
            #attack = int(v)
        #elif k == "会心率":
            #critical = int(v)
        #elif k == "会心ダメージ":
                #critical_hurt = int(v)
    #4つのステータス分回す
    for n in dict:
        #とりあえず関連するステータスかどうかのfor
        for k,v in n.items():
            if k == "攻撃力%":
                attack = str(v)
            elif k == "会心率":
                critical = str(v)
            elif k == "会心ダメージ":
                critical_hurt = str(v)
    #forが終わったら計算
    hoge = Decimal(critical)*2
    resalt = Decimal(attack) + Decimal(hoge) + Decimal(critical_hurt)
    return resalt