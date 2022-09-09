import discord
from discord.ui import Select,View
from discord.ext import commands,tasks
from discord.commands import SlashCommandGroup
import datetime
from lib.yamlutil import yaml
import copy
import lib.now as getTime
import math

l: list[discord.SelectOption] = []

class helpselectView(View):
    @discord.ui.select(
            placeholder="表示するヘルプコマンドを指定してね",
            options=[
                discord.SelectOption(
                    label="メインコマンド",
                    emoji="📰",
                    description="原神ステータスを確認できます。",
                    ),
                discord.SelectOption(
                    label="UIDリストコマンド",
                    emoji="📚",
                    description="忘れがちなUIDを保存してくれるコマンドです。"),
                discord.SelectOption(
                    label="祈願コマンド",
                    emoji="✨",
                    description="いわゆるガチャシミュレーターです。"),
                discord.SelectOption(
                    label="便利コマンド",
                    emoji="🧰",
                    description="今日の日替わり秘境など"),
        ])
    async def select_callback(self, select:discord.ui.Select, interaction):
        embed = discord.Embed(title=f"helpコマンド：{select.values[0]}",color=0x1e90ff)
        if select.values[0] == "メインコマンド":
            print(f"help - メインコマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"このbotのメインとなるコマンドです。",
                value=f"\
                    \n**・/genshinstat get**\n自分以外が見ることができない状態で原神のステータスを取得します。UIDリスト機能で、自分のUIDを登録しておくと簡単に使えます。原神の設定でキャラ詳細を公開にすると、キャラステータスも確認できます。\
                ")
        elif select.values[0] == "UIDリストコマンド":
            print(f"help - UIDリストコマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"いちいち確認するのが面倒なUIDを管理するコマンドです。",
                value=f"\
                    \n**・/uidlist get**\n登録され、公開設定が「公開」になっているUIDがここに表示されます。\
                    \n**・/uidlist control**\n登録したUIDを管理するパネルを表示します。UIDの登録や削除、公開設定の切り替えもここからできます。\
                ")
        elif select.values[0] == "祈願コマンド":
            print(f"help - 祈願コマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"いわゆるガチャシミュレーターです。天井もユーザーごとにカウントされています。",
                value=f"\
                    \n**・/wish character**\n原神のガチャ排出時に表示されるイラストを検索します。\
                    \n**・/wish get**\n原神のガチャを10連分引きます。演出をするかしないか設定できます。\
                    \n**・/wish get_n**\n原神のガチャを指定回数分（最大200回）連続で引きます。結果はまとめて表示します。\
                    "
                )
        elif select.values[0] == "便利コマンド":
            print(f"help - 便利コマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"botを活用する上で覚えておきたいコマンドたちです。",
                value=f"\
                    \n**・/genbot help**\n迷ったらこちらから確認しよう。\
                    \n**・/genbot today**\n今日の日替わり秘境（天賦本や武器突破素材）や、デイリー更新まであと何分？を表示！\
                    \n**・/genbot report**\nバグ・不具合報告はこちらからよろしくお願いいたします...\
                ")
        await interaction.response.edit_message(content=None,embed=embed,view=self)

class MyEmbed(discord.Embed):
    def __init__(self, day_of_week: str, url: str):
        super().__init__(title=f"{day_of_week}の日替わり秘境はこちら", color=0x1e90ff)
        self.set_image(url=url)

    def get_embed(self):
        embed = copy.deepcopy(self)

        now = datetime.datetime.now()
        #明日の5時
        min = getTime.daily - now 
        min = min / datetime.timedelta(minutes=1)
        resalt = f"{math.floor(min/60)}時間{math.floor(min % 60)}分"
        embed.add_field(inline=False,name="デイリー更新まで",value=f"```fix\nあと{resalt}```")
        #明日の1時
        min = getTime.hoyo - now
        min = min / datetime.timedelta(minutes=1)
        resalt = f"{math.floor(min/60)}時間{math.floor(min % 60)}分"
        embed.add_field(inline=False,name="HoYoLabログインボーナス更新まで",value=f"```fix\nあと{resalt}```")
        #曜日取得
        min = getTime.weekly - now
        #これで来週の月曜日まであと何分になった
        min = min / datetime.timedelta(minutes=1)
        #これでhourは時間を24で割ったあまりになる
        hour = min/60 % 24 
        resalt = f"{math.floor(min/60/24)}日{math.floor(hour)}時間{math.floor(min % 60)}分"
        embed.add_field(inline=False,name="週ボス等リセットまで",value=f"```fix\nあと{resalt}```")
        return embed

class DayOfWeekUnexploredRegion:
    def __init__(self, file_path: str):
        self.EMBEDS: dict[int, discord.Embed] = {}
        self.SELECT_OPTIONS: list[discord.SelectOption] = []
        data: dict = yaml(file_path).load_yaml()
        for k, v in data.items():
            self.__add_data(
                key=k, day_of_week=v["day_of_week"], url=v["url"])

    def __add_data(self, key, day_of_week, url):
        # embedの追加
        embed = MyEmbed(day_of_week=day_of_week,url=url)
        self.EMBEDS[key] = embed
        # optionsの追加
        self.SELECT_OPTIONS.append(
            discord.SelectOption(label=day_of_week, value=str(key)))

DATA = DayOfWeekUnexploredRegion("weekday.yaml")


class weekselectView(View):
    def __init__(self):
        self.weekday = datetime.date.today().weekday()
        # タイムアウトを5分に設定してタイムアウトした時にすべてのボタンを無効にする
        super().__init__(timeout=300, disable_on_timeout=True)

    @discord.ui.button(label="今日の秘境に戻る")
    async def today(self, _: discord.ui.Button, interaction: discord.Interaction):
        self.weekday = datetime.date.today().weekday()
        await interaction.response.edit_message(embed=DATA.EMBEDS[self.weekday].get_embed(), view=self)

    @discord.ui.button(label="次の日の秘境")
    async def nextday(self, _: discord.ui.Button, interaction: discord.Interaction):
        self.weekday = (self.weekday + 1) % 7
        await interaction.response.edit_message(embed=DATA.EMBEDS[self.weekday].get_embed(), view=self)

    @discord.ui.select(
        placeholder="確認したい曜日を選択",
        options=DATA.SELECT_OPTIONS
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        self.weekday = int(select.values[0])
        view = self
        print(
            f"実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\n日替わり - {self.weekday}")
        await interaction.response.edit_message(embed=DATA.EMBEDS[self.weekday].get_embed(), view=view)

#バグ報告モーダル
class ReportModal(discord.ui.Modal):
    def __init__(self,select:str):
        super().__init__(title="バグ報告",timeout=300,)
        self.select = select

        self.content = discord.ui.InputText(
            label="バグの内容",
            style=discord.InputTextStyle.paragraph,
            placeholder="どのような状況でしたか？",
            required=True,
        )
        self.add_item(self.content)
        self.resalt = discord.ui.InputText(
            label="バグによって生じたこと",
            style=discord.InputTextStyle.paragraph,
            placeholder="例：インタラクションに失敗した、メッセージが大量に表示された等",
            required=True,
        )
        self.add_item(self.resalt)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="読み込み中...")
        self.content = self.content.value
        self.resalt = self.resalt.value
        bugListYaml = yaml(path='bug.yaml')
        bugList = bugListYaml.load_yaml()
        for n in range(50):
            try:
                temp = bugList[n]
                continue
            except:
                hoge = n
                break
        now = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        try:
            bugList[hoge] = {"select":self.select,"userId":interaction.user.id,"userName":interaction.user.name,"serverId":interaction.guild.id,"serverName":interaction.guild.name,"time":now,"content":self.content,"resalt":self.resalt}
            bugListYaml.save_yaml(bugList)
            await interaction.edit_original_message(content=f"不具合を送信しました！ご協力ありがとうございます！\nbugTrackNumber:00{hoge}\nbugTrackName:{self.content}")
            return
        except:
            print("おい管理者！エラーでてんぞこの野郎！！！！")
            await interaction.edit_original_message(content=f"送信できませんでしたが、管理者にログを表示しました。修正までしばらくお待ちください")
            raise

class bugselectView(View):
    @discord.ui.select(
            placeholder="どのコマンドで不具合が出ましたか？",
            options=[
                discord.SelectOption(
                    label="/genbot",
                    description="help、today等",),
                discord.SelectOption(
                    label="/uidlist",
                    description="get、controle等",),
                discord.SelectOption(
                    label="/genshinstat",
                    description="get等"),
                discord.SelectOption(
                    label="/wish",
                    description="get、get_n等"),
        ])
    async def select_callback(self, select:discord.ui.Select, interaction):
        print(str(select.values[0]))
        await interaction.response.send_modal(ReportModal(select.values[0]))

class GenbotCog(commands.Cog):

    def __init__(self, bot):
        print('genbot_initしたよ')
        self.bot = bot
        getTime.init_reference_times() 
        print(f'＝＝＝＝＝＝＝＝＝＝＝＝＝日付を更新したんご＝＝＝＝＝＝＝＝＝＝＝＝＝\n{datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')   
        self.slow_count.start()

    genbot = SlashCommandGroup('genbot', 'test')

    @genbot.command(name='help', description='原神ステータスbotに困ったらまずはこれ！')
    async def chelp(self, ctx):
        embed = discord.Embed(title=f"helpコマンド：メインコマンド", color=0x1e90ff)
        embed.add_field(
            name=f"このbotのメインとなるコマンドです。",
            value=f"\
                \n**・/genshinstat get**\n自分以外が見ることができない状態で原神のステータスを取得します。UIDリスト機能で、自分のUIDを登録しておくと簡単に使えます。原神の設定でキャラ詳細を公開にすると、キャラステータスも確認できます。\
        ")
        view = helpselectView(timeout=None)
        # レスポンスで定義したボタンを返す
        await ctx.respond("確認したいコマンドのジャンルを選択してね", embed=embed, view=view, ephemeral=True)

    @genbot.command(name='today', description='今日の日替わり秘境などをまとめて確認！')
    async def today(self, ctx):

        view = weekselectView()
        weekday = view.weekday
        embed = DATA.EMBEDS[weekday].get_embed()
        await ctx.respond(embed=embed, view=view, ephemeral=True)
        print(f"\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\ntoday - 今日の日替わり秘境")

    @genbot.command(name='report', description='不具合報告はこちらから！')
    async def report(self, ctx):

        view = bugselectView()
        await ctx.respond(view=view, ephemeral=True)
        print(f"\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nreport - 不具合報告")

    tz = datetime.timezone(offset=datetime.timedelta(hours=9))

    @tasks.loop(time=[datetime.time(hour=5, second=1, tzinfo=tz), datetime.time(hour=1, second=1, tzinfo=tz)]) 
    async def slow_count(self): 
        getTime.init_reference_times() 
        print(f'＝＝＝＝＝＝＝＝＝＝＝＝＝日付を更新したんご＝＝＝＝＝＝＝＝＝＝＝＝＝\n{datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')   

def setup(bot):
    bot.add_cog(GenbotCog(bot))