from decimal import Decimal
from enums.substatus import SubTypes


def score(artifact_status: list[tuple[str, str]], build_type: str):
    resalt = Decimal(0)
    special_status = Decimal(0)
    critical = Decimal(0)
    critical_hurt = Decimal(0)

    # 4つのステータス分回す
    for n in artifact_status:
        k = n[0]
        v = n[1]
        # とりあえず関連するステータスかどうかのfor
        if k == build_type:  # 特定のスコア
            special_status = Decimal(v)
        elif k == SubTypes.CRITICAL.value:  # 会心率（2倍）
            critical = Decimal(v) * Decimal(2)
        elif k == SubTypes.CRITICAL_HURT.value:  # 会心ダメ
            critical_hurt = Decimal(v)
    # forが終わったら計算
    resalt = sum((special_status, critical, critical_hurt,))
    # 元素熟知の時のみ2で割って合わせます
    if build_type == SubTypes.ELEMENT_MASTERY.value:
        resalt /= Decimal(2)
    return round(resalt, 1)

# 元素チャージ → Ch: 1, 率: 2, ダメ: 1
# 防御 →  防御率: 1, 率: 2, ダメ: 1
# HP型 → HP: 1, 率:2, ダメ: 1
# 熟知型 → 元素熟知: 1/2, 率: 1, ダメ: 1/2
