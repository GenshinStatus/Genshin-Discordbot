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
        super().__init__(title="あなたのUIDを入力してください。",timeout=None,)
        self.ctx = ctx

        self.uid = discord.ui.InputText(
            label="UID",
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
            await interaction.response.send_message(f"エラー：UIDを入力してください。", ephemeral=True)
        view = isPablicButton(self.uid,self.ctx)
        await interaction.response.send_message(f"{self.uid}を登録します。UIDは公開しますか？",view=view, ephemeral=True)
        return

#公開するかどうかを聞くボタン
class isPablicButton(View):
    def __init__(self, uid: str, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.uid = uid

    @discord.ui.button(label="公開する", style=discord.ButtonStyle.green)
    async def callback(self, button, interaction: discord.Interaction):
        isPablic = True
        try:
            name = await uid_set(self.ctx,self.uid,isPablic)
        except KeyError:
            await interaction.response.send_message(f"{self.uid}はUIDではありません。",ephemeral=True)
        await interaction.response.send_message(f"{self.uid}を公開設定で登録しました！",ephemeral=True)

    @discord.ui.button(label="公開しない", style=discord.ButtonStyle.red)
    async def no_callback(self, button, interaction: discord.Interaction):
        isPablic = False
        try:
            name = await uid_set(self.ctx,self.uid,isPablic)
        except KeyError:
            await interaction.response.send_message(f"{self.uid}はUIDではありません。",ephemeral=True)
        await interaction.response.send_message(f"{self.uid}を非公開設定で登録しました！",ephemeral=True)

#モーダルを表示させるボタン
class UidModalButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="UIDを登録する",style=discord.ButtonStyle.green)
        self.ctx = ctx
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UidModal(self.ctx))

#UIDを登録する関数
async def uid_set(ctx,uid,isPablic):
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
    if isPablic == True:
        isPablic = "True"
    elif isPablic == False:
        isPablic = "False"
    uidList[serverId][uid] = {"user":ctx.author.name,"name":name,"isPablic":isPablic}
    print(uidList)
    uidListYaml.save_yaml(uidList)
    return name

class uidListCog(commands.Cog):

    def __init__(self, bot):
        print('uidList初期化')
        self.bot = bot

    uidlist = SlashCommandGroup('uidlist', 'test')

    @uidlist.command(name="get", description="UIDリストの操作パネルを開きます。")
    async def uidlist_register(
            self,
            ctx: discord.ApplicationContext,
    ):
        await ctx.respond("読み込み中", ephemeral=True, delete_after=10)
        serverId = ctx.guild.id
        embed = discord.Embed( 
                    title=f"UIDリスト",
                    description="UIDを登録する際に公開設定にするとここに表示されます。",
                    color=0x1e90ff, 
                    )
        for k,v in uidList[serverId].items():
            try:
                if v["isPablic"] == "False":
                    continue
            except:
                continue
            embed.add_field(inline=False,name=k,value=f"Discord：{v['user']}\nユーザー名：{v['name']}")
        
        view = View()
        button = UidModalButton(ctx)
        view.add_item(button)
        await ctx.send(embed=embed,view=view)

def setup(bot):
    bot.add_cog(uidListCog(bot))