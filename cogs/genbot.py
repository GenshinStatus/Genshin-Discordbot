import discord
from discord.ui import Select,View
from discord.ext import commands
from discord.commands import SlashCommandGroup
import datetime

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
        ])
    async def select_callback(self, select:discord.ui.Select, interaction):
        embed = discord.Embed(title=f"helpコマンド：{select.values[0]}",color=0x1e90ff)
        if select.values[0] == "メインコマンド":
            print("help - メインコマンド")
            embed.add_field(
                name=f"このbotのメインとなるコマンドです。",
                value=f"\
                    \n**・/genshinstat get**\n自分以外が見ることができない状態で原神のステータスを取得します。UIDリスト機能で、自分のUIDを登録しておくと簡単に使えます。原神の設定でキャラ詳細を公開にすると、キャラステータスも確認できます。\
                ")
        elif select.values[0] == "UIDリストコマンド":
            print("help - UIDリストコマンド")
            embed.add_field(
                name=f"いちいち確認するのが面倒なUIDを管理するコマンドです。",
                value=f"\
                    \n**・/uidlist get**\n登録され、公開設定が「公開」になっているUIDがここに表示されます。\
                    \n**・/uidlist control**\n登録したUIDを管理するパネルを表示します。UIDの登録や削除、公開設定の切り替えもここからできます。\
                ")
        elif select.values[0] == "祈願コマンド":
            print("help - 祈願コマンド")
            embed.add_field(
                name=f"いわゆるガチャシミュレーターです。天井もユーザーごとにカウントされています。",
                value=f"\
                    \n**・/wish character**\n原神のガチャ排出時に表示されるイラストを検索します。\
                    \n**・/wish get**\n原神のガチャを10連分引きます。演出をするかしないか設定できます。\
                    \n**・/wish get_n**\n原神のガチャを指定回数分（最大200回）連続で引きます。結果はまとめて表示します。\
                    "
                )
        await interaction.response.edit_message(content=None,embed=embed,view=self)

#今日の秘境を確認するボタン
class todayButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="今日の秘境に戻る",style=discord.ButtonStyle.green)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        today = datetime.date.today()
        hoge = today.weekday()
        embed = discord.Embed(title=f"本日の日替わり秘境はこちら！",color=0x1e90ff)
        embed.set_image(url=f"attachment://hoge.png") 
        await interaction.response.edit_message(embed=embed,file=await getDatatime(hoge),view=weekselectView())

#明日にするボタン
class weekselectView(View):
    def __init__(self):
        self.add_item(todayButton)
        hoge = ["月曜日","火曜日","水曜日","木曜日","金曜日","土曜日","日曜日"]
        global l
        for v in range(6):
            l.append(discord.SelectOption(label=hoge[v],value=str(v)))

    @discord.ui.select(
            placeholder="確認したい曜日を選択",
            options=l
    )

    async def select_callback(self, select:discord.ui.Select, interaction:discord.Interaction):
        embed = discord.Embed(title=f"{select.values[0]}の日替わり秘境はこちら！",color=0x1e90ff)
        embed.set_image(url=f"attachment://hoge.png") 
        view = self
        print(f"実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\n日替わり - {select.values[0]}")
        await interaction.response.edit_message(embed=embed,file=await getDatatime(int(select.values[1])),view=view)

async def getDatatime(hoge):
        if hoge == 0:
            hoge = discord.File("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\today\\Monday.png", f"hoge.png")
        if hoge == 1:
            hoge = discord.File("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\today\\Tuesday.png", f"hoge.png")
        if hoge == 2:
            hoge = discord.File("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\today\\Wednesday.png", f"hoge.png")
        if hoge == 3:
            hoge = discord.File("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\today\\Thursday.png", f"hoge.png")
        if hoge == 4:
            hoge = discord.File("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\today\\Friday.png", f"hoge.png")
        if hoge == 5:
            hoge = discord.File("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\today\\Saturday.png", f"hoge.png")
        if hoge == 6:
            hoge = discord.File("C:\\Users\\Cinnamon\\Desktop\\DebugGenshinNetwork\\Image\\today\\Sunday.png", f"hoge.png")
        return hoge

class GenbotCog(commands.Cog):

    def __init__(self, bot):
        print('genbot_initしたよ')
        self.bot = bot

    genbot = SlashCommandGroup('genbot', 'test')

    @genbot.command(name='help', description='原神ステータスbotに困ったらまずはこれ！')
    async def chelp(self, ctx):
        embed = discord.Embed(title=f"helpコマンド：メインコマンド",color=0x1e90ff)
        embed.add_field(
            name=f"このbotのメインとなるコマンドです。",
            value=f"\
                \n**・/genshinstat get**\n自分以外が見ることができない状態で原神のステータスを取得します。UIDリスト機能で、自分のUIDを登録しておくと簡単に使えます。原神の設定でキャラ詳細を公開にすると、キャラステータスも確認できます。\
        ")
        view = helpselectView(timeout=None)
        await ctx.respond("確認したいコマンドのジャンルを選択してね",embed=embed,view=view,ephemeral=True)  # レスポンスで定義したボタンを返す

    @genbot.command(name='today', description='今日の日替わり秘境などをまとめて確認！')
    async def today(self, ctx):
        today = datetime.date.today()
        hoge = today.weekday()
        embed = discord.Embed(title=f"本日の日替わり秘境はこちら！",color=0x1e90ff)
        embed.set_image(url=f"attachment://hoge.png") 
        await ctx.respond(embed=embed,file=await getDatatime(hoge),view=weekselectView(),ephemeral=True)

def setup(bot):
    bot.add_cog(GenbotCog(bot))