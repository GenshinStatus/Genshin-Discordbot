
import discord
import datetime

class nowEmbed(discord.Embed):
    def __init__(self):
        super().__init__()

    async def now(self,day_of_week):
        now = datetime.datetime.now()
        embed = discord.Embed(
            title=f"{day_of_week}の日替わり秘境はこちら", color=0x1e90ff, description=now.strftime('%Y年%m月%d日 %H:%M:%S'))
        #現在の時間+1日
        daily = now + datetime.timedelta(days=1)

        #明日の5時
        daily = datetime.datetime(daily.year, daily.month, daily.day, 5, 00, 00, 0000)
        hoge = daily - now
        hour = round(hoge / datetime.timedelta (hours=1)) - hoge.days*24 
        resalt = f"{hour}時間{round(hoge.seconds/60)-hour*60}分"
        embed.add_field(inline=False,name="デイリー更新まで",value=f"```あと{resalt}```")
        
        #明日の1時
        daily = datetime.datetime(daily.year, daily.month, daily.day, 1, 00, 00, 0000)
        hoge = daily - now
        hour = round(hoge / datetime.timedelta (hours=1)) - hoge.days*24
        resalt = f"{hour}時間{round(hoge.seconds/60)-hour*60}分"
        embed.add_field(inline=False,name="HoYoLabログインボーナス更新まで",value=f"```あと{resalt}```")
        
        #曜日取得
        weekday = datetime.date.today().weekday()
        
        #7から曜日を引いた日後が来週の月曜日
        hoge = 7-weekday
        nextWeek = now + datetime.timedelta(days=hoge)
        nextWeek = datetime.datetime(nextWeek.year, nextWeek.month, nextWeek.day, 0, 00, 00, 0000)
        hoge = nextWeek - now
        hour = round(hoge / datetime.timedelta (hours=1)) - hoge.days*24
        resalt = f"{hoge.days}日{hour}時間{round(hoge.seconds/60)-hour*60}分"
        embed.add_field(inline=False,name="週ボス等リセットまで",value=f"```あと{resalt}```")

        return embed