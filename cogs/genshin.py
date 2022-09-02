from http import server
import discord
from discord.ui import Select,View,Button
from discord.ext import commands
from discord import Option, SlashCommandGroup
import aiohttp
from lib.yamlutil import yaml
import lib.getStat as getStat
import lib.picture as getPicture
from typing import List

dataYaml = yaml(path='genshin_avater.yaml')
data = dataYaml.load_yaml()
charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinJp = genshinJpYaml.load_yaml()
uidListYaml = yaml(path='uidList.yaml')
uidList = uidListYaml.load_yaml()
l: list[discord.SelectOption] = []

class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, label: str, uid: str, dict, data):
        super().__init__(style=discord.ButtonStyle.secondary, label=label)
        self.dict = dict
        self.uid = uid
        self.data = data

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view

        self.style = discord.ButtonStyle.success
        content = self.label
        #ラベル（名前）からIDを割り出す
        #多分「名前：iD」ってなってるはず
        id = self.dict[self.label]
        print(interaction.user.name)
        for child in self.view.children:
            child.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(content=content, embed=await getStat.get(self.uid, id), view=TicTacToe(self.data,self.uid))

class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]

    def __init__(self, data, uid):
        super().__init__(timeout=None)
        names = []
        dict = {}
        #入ってきたidを名前にしてリスト化
        for id in data:
            id = str(id)
            name = genshinJp[characters[str(id)]["NameId"]]
            names.append(name)
            dict.update({name: id})
        #名前をラベル、ついでにdictとuidも送り付ける
        for v in names:
            self.add_item(TicTacToeButton(v,uid,dict,data))

class GenshinCog(commands.Cog):

    def __init__(self, bot):
        print('genshin初期化')
        self.bot = bot

    async def getApi(self,uid,resp):
        try:
            embed = discord.Embed( 
                                title=f"{resp['playerInfo']['nickname']}",
                                color=0x1e90ff, 
                                description=f"uid: {uid}", 
                                url=f"https://enka.network/u/{uid}/__data.json"
                                )
            embed.set_image(url=f"attachment://{uid}.png")                     
            return embed
        except:
            embed = discord.Embed( 
                    title=f"エラーが発生しました。APIを確認してからもう一度お試しください。\n{f'https://enka.network/u/{uid}/__data.json'}",
                    color=0x1e90ff, 
                    url=f"https://enka.network/u/{uid}/__data.json"
                    )
            return embed

    genshin = SlashCommandGroup('genshinstat', 'test')

    @genshin.command(name="get", description="UIDからキャラ情報を取得します")
    async def genshin_get(
            self,
            ctx: discord.ApplicationContext,
            uid: Option(str, required=True, description='UIDを入力してください．'),
    ):
        msg = await ctx.respond(content="アカウント情報読み込み中...", ephemeral=False)  
        url = f"https://enka.network/u/{uid}/__data.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.json()
                resalt = []
        embed = await GenshinCog.getApi(self,uid,resp)
        await msg.edit_original_message(content="キャラ情報読み込み中...")  

        for id in resp["playerInfo"]["showAvatarInfoList"]:
            resalt.append(id["avatarId"])
        await msg.edit_original_message(content="画像を生成中...")  
        hoge = discord.File(await getPicture.getProfile(uid,resp), f"{uid}.png")
        await msg.edit_original_message(content="ボタンを生成中...")  
        await msg.edit_original_message(content=None,embed=embed,view=TicTacToe(resalt,uid), file=hoge)

    @genshin.command(name="get_private", description="【自分しか見れません】UIDからキャラ情報を取得します")
    async def genshin_get_private(
            self,
            ctx: discord.ApplicationContext,
            uid: Option(str, required=True, description='UIDを入力してください．'),
    ):
        await ctx.respond(content="アカウント情報読み込み中...", ephemeral=True)  
        url = f"https://enka.network/u/{uid}/__data.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.json()
                resalt = []
        embed = await GenshinCog.getApi(self,uid,resp)
        await ctx.respond(content="キャラ情報読み込み中...", ephemeral=True)  

        for id in resp["playerInfo"]["showAvatarInfoList"]:
            resalt.append(id["avatarId"])
        await ctx.respond(content="画像を生成中...",ephemeral=True)  
        hoge = discord.File(await getPicture.getProfile(uid,resp), f"{uid}.png")
        await ctx.respond(content="ボタンを生成中...",ephemeral=True)  
        await ctx.respond(content=None,embed=embed,view=TicTacToe(resalt,uid),file=hoge,ephemeral=True)

    @genshin.command(name="uid_register", description="何かと忘れがちなUIDを登録します")
    async def genshin_uid_register(
            self,
            ctx: discord.ApplicationContext,
            uid: Option(str, required=True, description='UIDを入力してください．'),
    ):
        await ctx.respond(content="アカウント情報読み込み中...", ephemeral=True)  
        url = f"https://enka.network/u/{uid}/__data.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.json()
        serverId = ctx.guild.id
        print(serverId)
        name = resp['playerInfo']['nickname']
        print(name)
        if not serverId in uidList:
            uidList[serverId] = dict()
        uidList[serverId][uid] = {"user":ctx.author.name,"name":name}
        print(uidList)
        uidListYaml.save_yaml(uidList)
        await ctx.respond(content=f"UIDリストに追加しました！\nuid：{uid}\n原神ユーザー名：{name}")

    @genshin.command(name="uid", description="登録されたUIDを一覧で表示します")
    async def genshin_uid(
            self,
            ctx: discord.ApplicationContext,
    ):
        await ctx.respond(content="アカウント情報読み込み中...", ephemeral=True)  
        serverId = ctx.guild.id
        embed = discord.Embed( 
                    title=f"UIDリスト",
                    color=0x1e90ff, 
                    )
        for k,v in uidList[serverId].items():
            embed.add_field(inline=False,name=k,value=f"Discord：{v['user']}\nユーザー名：{v['name']}")
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(GenshinCog(bot))