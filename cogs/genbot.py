import discord
from discord.ui import Select,View
from discord.ext import commands
from discord.commands import SlashCommandGroup

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
        await ctx.respond("確認したいコマンドのジャンルを選択してね",embed=embed,view=view)  # レスポンスで定義したボタンを返す

def setup(bot):
    bot.add_cog(GenbotCog(bot))