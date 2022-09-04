from calendar import c
from http import server
from re import U
import discord
from discord.ui import Select,View,Button,Modal
from discord.ext import commands
from discord import Option, SlashCommandGroup
import aiohttp
from lib.yamlutil import yaml
import lib.getStat as getStat
import lib.picture as getPicture
from typing import List

uidListYaml = yaml(path='uidList.yaml')
uidList = uidListYaml.load_yaml()
l: list[discord.SelectOption] = []

#UIDを聞くモーダル
class UidModal(discord.ui.Modal):
    def __init__(self,ctx):
        super().__init__(title="あなたのUIDを入力してください。",timeout=300,)
        self.ctx = ctx

        self.uid = discord.ui.InputText(
            label="UIDを半角数字で入力してください。",
            style=discord.InputTextStyle.short,
            min_length=9,
            max_length=9,
            placeholder="000000000",
            required=True,
        )
        self.add_item(self.uid)

    async def callback(self, interaction: discord.Interaction) -> None:
        self.uid = self.uid.value
        if self.uid == "000000000":
            await interaction.response.edit_message(f"エラー：UIDを入力してください。")
        view = isPablicButton(self.uid,self.ctx)
        await interaction.response.edit_message(content=f"{self.uid}を登録します。UIDは公開しますか？",view=view)
        return

#公開するかどうかを聞くボタン
class isPablicButton(View):
    def __init__(self, uid: str, ctx):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.uid = uid

    @discord.ui.button(label="公開する", style=discord.ButtonStyle.green)
    async def callback(self, button, interaction: discord.Interaction):
        isPablic = True
        try:
            name = await uid_set(self.ctx,self.uid,isPablic)
        except KeyError:
            await interaction.response.edit_message(content=f"{self.uid}はUIDではありません。",view=None)
            return
        embed = await getEmbed(self.ctx)
        if name == "hoge":
            await interaction.response.edit_message(content=None,embed=None,view=None)
        await interaction.response.edit_message(content=name,embed=embed[0],view=None)

    @discord.ui.button(label="公開しない", style=discord.ButtonStyle.red)
    async def no_callback(self, button, interaction: discord.Interaction):
        isPablic = False
        try:
            name = await uid_set(self.ctx,self.uid,isPablic)
        except KeyError:
            await interaction.response.edit_message(content=f"{self.uid}はUIDではありません。",view=None)
            return
        embed = await getEmbed(self.ctx)
        if name == "hoge":
            await interaction.response.edit_message(content=None,embed=None,view=None)
        await interaction.response.edit_message(content=name,embed=embed[0],view=None)

#モーダルを表示させるボタン
class UidModalButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="UIDを登録する",style=discord.ButtonStyle.green)
        self.ctx = ctx
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UidModal(self.ctx))

#UIDを削除するかどうか聞くボタン
class isDeleteButton(discord.ui.Button):
    def __init__(self, ctx, uid):
        super().__init__(label="UIDを削除する",style=discord.ButtonStyle.red)
        self.ctx = ctx
        self.uid = uid
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="UIDを登録すれば、各種コマンドの入力が省かれ、便利になります。\n**本当に削除しますか？**",view=isDeleteEnterButton(self.uid,self.ctx))

#本当にUIDを削除するかどうか聞くボタン
class isDeleteEnterButton(View):
    def __init__(self, uid: str, ctx):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.uid = uid

    @discord.ui.button(label="削除する", style=discord.ButtonStyle.red)
    async def callback(self, button, interaction: discord.Interaction):
        try:
            uid = await uid_del(self.ctx,self.uid)
        except:
            await interaction.response.edit_message(f"{self.uid}を何らかの理由で削除できませんでした。\nよろしければ、botのプロフィールからエラーの報告をお願いします。")
            raise
        self.clear_items()
        await interaction.response.edit_message(content=f"{uid}を削除しました。",embed=None,view=self)

    @discord.ui.button(label="キャンセルする", style=discord.ButtonStyle.green)
    async def no_callback(self, button, interaction: discord.Interaction):
        self.clear_items()
        await interaction.response.edit_message(content="削除がキャンセルされました",view=self)

#UIDを公開するかどうか聞くボタン
class isPabricEnterButton(discord.ui.Button):
    def __init__(self, ctx, uid):
        super().__init__(label="公開設定変更",style=discord.ButtonStyle.gray)
        self.ctx = ctx
        self.uid = uid
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="UIDを公開すると、UIDリストに表示されたり、他のユーザーがあなたのステータスを確認することができるようになります",view=isPablicButton(self.uid,self.ctx))

#UIDを登録する関数
async def uid_set(ctx,uid,isPablic):
    uidListYaml = yaml(path='uidList.yaml')
    uidList = uidListYaml.load_yaml()   
    url = f"https://enka.network/u/{uid}/__data.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            resp = await response.json()
    serverId = ctx.guild.id
    print(ctx.guild.name)
    name = resp['playerInfo']['nickname']
    print(name)
    if not serverId in uidList:
        uidList[serverId] = dict()
    try:
        if uidList[serverId][uid]["user"] != ctx.author.name:
            await ctx.send("このUIDはすでに他の人によって登録されています")
            return "hoge"
    except:
        print(ctx.author.name)
    if isPablic == True:
        isPablic = "True"
    elif isPablic == False:
        isPablic = "False"
    uidList[serverId][uid] = {"user":ctx.author.name,"name":name,"isPablic":isPablic}
    print(uidList)
    uidListYaml.save_yaml(uidList)
    if isPablic == "True":
        name = f"{uid}を公開設定で登録しました！"
    elif isPablic == "False":
        name = f"{uid}を非公開設定で登録しました！"
    return name

#UIDを削除する関数
async def uid_del(ctx,uid):
    uidListYaml = yaml(path='uidList.yaml')
    uidList = uidListYaml.load_yaml()
    serverId = ctx.guild.id
    print(serverId)
    uidList[serverId].pop(uid)
    print(uidList)
    uidListYaml.save_yaml(uidList)
    return uid

#UIDが公開設定かどうか調べてくれる関数
async def uid_isPablic(ctx,uid):
    serverId = ctx.guild.id
    print(ctx.guild.name)
    try:
        isPablic = uidList[serverId][uid]["isPablic"]
    except:
        isPablic = False
    if isPablic == "True":
        isPablic = True
    elif isPablic == "False":
        isPablic = False
    return isPablic

async def getEmbed(ctx):
    serverId = ctx.guild.id
    hoge = None
    view = View()
    uidListYaml = yaml(path='uidList.yaml')
    uidList = uidListYaml.load_yaml()
    
    # もしuserに当てはまるUIDが無ければ終了
    try:
        for k,v in uidList[serverId].items():
            if v["user"] == ctx.author.name:
                hoge = k
    except:
        print(ctx.guild.name)
        hoge = None
    if hoge == None:
        button = UidModalButton(ctx)
        view.add_item(button)
        await ctx.respond(content="UIDが登録されていません。下のボタンから登録してください。",view=view,ephemeral=True)
        return

    #原神ユーザー名取得
    user = uidList[serverId][hoge]["name"]
    
    embed = discord.Embed( 
                title=f"登録情報・{user}",
                description=f"UID:{hoge}",
                color=0x1e90ff, 
                )
    try:
        if v["isPablic"] == "False":
            isPablic = "非公開です"
        elif v["isPablic"] == "True":
            isPablic = "公開されています"
    except:
        isPablic = "未設定（非公開）です"
    embed.add_field(inline=False,name="UID公開設定",value=isPablic)
    return embed,hoge

class uidListCog(commands.Cog):

    def __init__(self, bot):
        print('uidList初期化')
        self.bot = bot

    uidlist = SlashCommandGroup('uidlist', 'test')

    @uidlist.command(name="get", description="UIDリストを開きます。")
    async def uidlist_get(
            self,
            ctx: discord.ApplicationContext,
    ):
        uidListYaml = yaml(path='uidList.yaml')
        uidList = uidListYaml.load_yaml()
        serverId = ctx.guild.id
        embed = discord.Embed( 
                    title=f"UIDリスト",
                    description="UIDを登録する際に公開設定にするとここに表示されます。",
                    color=0x1e90ff, 
                    )
        try:
            for k,v in uidList[serverId].items():
                try:
                    if v["isPablic"] == "False":
                        continue
                except:
                    continue
                embed.add_field(inline=False,name=k,value=f"Discord：{v['user']}\nユーザー名：{v['name']}")
        except:
            print(ctx.guild.name)
        
        view = View()
        try:
            for k,v in uidList[serverId].items():
                if v["user"] == ctx.author.name:
                    await ctx.respond(embed=embed,ephemeral=True)
                    return
        except:
            print(ctx.guild.name)
        button = UidModalButton(ctx)
        view.add_item(button)
        await ctx.respond(embed=embed,view=view,ephemeral=True)

    @uidlist.command(name="control", description="登録したUIDの操作パネルを開きます。")
    async def uidlist_control(
            self,
            ctx: discord.ApplicationContext,
    ):
        embed = await getEmbed(ctx)
        k = embed[1]
        view = View()
        view.add_item(isDeleteButton(ctx,uid=k))
        view.add_item(isPabricEnterButton(ctx,k))
        await ctx.respond(embed=embed[0],view=view,ephemeral=True)

def setup(bot):
    bot.add_cog(uidListCog(bot))