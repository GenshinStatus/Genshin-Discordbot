from datetime import datetime, timedelta

daily = 0
weekly = 0
hoyo = 0


def init_reference_times():
    """
    daily, hoyolab, weeklyの基準時間を初期化します
    """
    global daily
    global weekly
    global hoyo

    one_day = timedelta(days=1)
    seven_days = timedelta(days=7)
    now = datetime.now()
    daily = datetime(year=now.year, month=now.month, day=now.day, hour=5)
    if daily < now:
        daily += one_day
    hoyo = datetime(year=now.year, month=now.month, day=now.day, hour=1)
    if hoyo < now:
        hoyo += one_day
    weekly = datetime(year=now.year, month=now.month, day=now.day,
                      hour=5) + timedelta(days=(7-now.weekday()) % 7)
    if weekly < now:
        weekly += seven_days
