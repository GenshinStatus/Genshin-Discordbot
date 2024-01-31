import discord
from discord.ui import Select, View, Button, Modal
from discord.ext import commands
from discord import Option, SlashCommandGroup
import aiohttp
import lib.sql as SQL
from lib import enkaconnecter

l: list[discord.SelectOption] = []

# UIDを聞くモーダル


class UidModal(discord.ui.Modal):
    def __init__(self, ctx):
        super().__init__(title="あなたのUIDを入力してください。", timeout=300,)
        self.ctx = ctx

        self.uid = discord.ui.InputText(
            label="UIDを半角数字で入力してください。",
            style=discord.InputTextStyle.short,
            min_length=9,
            max_length=10,
            placeholder="000000000",
            required=True,
        )
        self.add_item(self.uid)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content=f"処理中です...", embed=None, view=None)
        view = isPablicButton(self.ctx)
        try:
            self.uid = int(self.uid.value)
            is_first_registration = SQL.User.get_user_list(self.ctx.author.id)
            await uid_set(self.ctx, self.uid)
        except Exception as e:
            print(e)
            # await interaction.edit_original_response(content=f"{self.uid}はUIDではありません。", embed=None, view=None)
            await interaction.edit_original_response(content=f"UIDが無効か、EnkaNetworkがメンテナンス中です。", embed=None, view=None)
            return
        if is_first_registration == []:
            await interaction.edit_original_response(content=f"{self.uid}を登録します。\nUIDを公開すると、UIDリストに表示されるようになります\n※UIDを複数登録している場合は個別で設定することはできません。", view=view)
        else:
            embed = await getEmbed(self.ctx)
            await interaction.edit_original_response(content="登録しました！", embed=embed, view=None)
            print(
                f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - 公開")
        return

# 公開するかどうかを聞くボタン


class isPablicButton(View):
    def __init__(self, ctx):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.ctx = ctx

    @discord.ui.button(label="公開する", style=discord.ButtonStyle.green)
    async def callback(self, button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="処理中です...", view=None)
        SQL.PermitID.add_permit_id(self.ctx.guild.id, self.ctx.author.id)
        embed = await getEmbed(self.ctx)
        await interaction.edit_original_response(content="公開しました！\nUIDは`/uidlist controle`から管理できます。", embed=embed, view=None)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - 公開")

    @discord.ui.button(label="公開しない", style=discord.ButtonStyle.red)
    async def no_callback(self, button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="処理中です...", view=None)
        SQL.PermitID.remove_permit_id(self.ctx.guild.id, self.ctx.author.id)
        embed = await getEmbed(self.ctx)
        await interaction.edit_original_response(content="非公開にしました！\nUIDは`/uidlist controle`から管理できます。", embed=embed, view=None)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - 非公開")

# モーダルを表示させるボタン


class UidModalButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="UIDを登録する", style=discord.ButtonStyle.green)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UidModal(self.ctx))
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - UIDモーダル表示")

# UIDを削除するかどうか聞くボタン


class isDeleteButton(discord.ui.Button):
    def __init__(self, ctx, uid):
        super().__init__(label="UIDを削除する", style=discord.ButtonStyle.red)
        self.ctx = ctx
        self.uid = uid

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=f"UIDを登録すれば、各種コマンドの入力が省かれ、便利になります。\n**本当に削除しますか？**\n削除しようとしているUID：{self.uid}", view=isDeleteEnterButton(self.uid, self.ctx), embed=None)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - 削除するかどうか")

# 本当にUIDを削除するかどうか聞くボタン


class isDeleteEnterButton(View):
    def __init__(self, uid: str, ctx):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.ctx = ctx
        self.uid = uid

    @discord.ui.button(label="削除する", style=discord.ButtonStyle.red)
    async def callback(self, button, interaction: discord.Interaction):
        try:
            uid = await uid_del(self.ctx, self.uid)
        except:
            await interaction.response.edit_message(content=f"{self.uid}を何らかの理由で削除できませんでした。\nよろしければ、botのプロフィールからエラーの報告をお願いします。", embed=None, view=None)
            raise
        self.clear_items()
        await interaction.response.edit_message(content=f"{uid}を削除しました。", embed=None, view=self)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - 削除")

    @discord.ui.button(label="キャンセルする", style=discord.ButtonStyle.green)
    async def no_callback(self, button, interaction: discord.Interaction):
        self.clear_items()
        await interaction.response.edit_message(content="削除がキャンセルされました", view=self)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - キャンセル")

# UIDを公開するかどうか聞くボタン


class isPabricEnterButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="公開設定変更", style=discord.ButtonStyle.gray)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="UIDを公開すると、UIDリストに表示されるようになります\n※UIDを複数登録している場合は個別で設定することはできません。", view=isPablicButton(self.ctx))

# UIDを登録する関数


async def uid_set(ctx, uid):
    resp = await enkaconnecter.get_data(uid)
    print(ctx.guild.name)
    name = resp['playerInfo']['nickname']
    print(name)
    userData = SQL.User(ctx.author.id, uid, name)
    SQL.User.insert_user(userData)
    return

# UIDを削除する関数


async def uid_del(ctx, uid):
    serverId = ctx.guild.id
    SQL.User.delete_user(ctx.author.id, uid)
    return uid


async def getEmbed(ctx):
    serverId = ctx.guild.id
    view = View(timeout=300, disable_on_timeout=True)

    # もしuserに当てはまるUIDが無ければ終了
    uidList = SQL.User.get_user_list(ctx.author.id)
    isPublic = SQL.PermitID.is_user_public(ctx.guild.id, ctx.author.id)
    if isPublic == False:
        isPublic = "非公開です"
    elif isPublic == True:
        isPublic = "公開されています"
    embed = discord.Embed(
        title=f"登録情報",
        description=f"{len(uidList)}個のUIDが登録されています。\n公開設定: {isPublic}",
        color=0x1e90ff,
    )
    for v in uidList:
        embed.add_field(
            inline=False, name=f"ユーザー名・{v.game_name}", value=f"UID: {v.uid}")
    return embed


class select_uid_pulldown(discord.ui.Select):
    def __init__(self, ctx, selectOptions: list[discord.SelectOption], game_name):
        super().__init__(placeholder="削除するUIDを選択してください", options=selectOptions)
        self.ctx = ctx
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="削除しようとしているUID", description=f"UID:{self.values[0]}\nユーザー名:{self.game_name}", color=0x1e90ff, )
        await interaction.response.edit_message(content=f"UIDを登録すれば、各種コマンドの入力が省かれ、便利になります。\n**本当に削除しますか？**\n", view=isDeleteEnterButton(int(self.values[0]), self.ctx), embed=embed)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - 削除するかどうか")


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
        embed = discord.Embed(
            title=f"UIDリスト",
            description="UIDを登録する際に公開設定にするとここに表示されます。",
            color=0x1e90ff,
        )
        uidList = SQL.PermitID.get_uid_list(ctx.guild.id)
        for v in uidList:
            embed.add_field(inline=False, name=v.uid,
                            value=f"Discord： <@{v.d_id}>\nユーザー名：{v.g_name}")
        view = View(timeout=300, disable_on_timeout=True)
        try:
            for v in uidList:
                if v.d_name == ctx.author.name:
                    await ctx.respond(embed=embed, ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
                    print(
                        f"==========\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nuidlist - 取得")
                    return
        except:
            print(ctx.guild.name)
        button = UidModalButton(ctx)
        view.add_item(button)
        await ctx.respond(embed=embed, view=view, ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
        print(
            f"==========\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nuidlist - 未登録取得")

    @uidlist.command(name="control", description="登録したUIDの操作パネルを開きます。")
    async def uidlist_control(
            self,
            ctx: discord.ApplicationContext,
    ):
        try:
            embed = await getEmbed(ctx)
            select_options: list[discord.SelectOption] = []
            userData = SQL.User.get_user_list(ctx.author.id)
            if userData == []:
                view = View(timeout=300, disable_on_timeout=True)
                button = UidModalButton(ctx)
                view.add_item(button)
                await ctx.respond(content="UIDが登録されていません。下のボタンから登録してください。", view=view, ephemeral=True)
                print(
                    f"==========\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nuidcontrole - 登録してくれ")
                return
            for v in userData:
                select_options.append(
                    discord.SelectOption(label=v.game_name, description=str(v.uid), value=str(v.uid)))
            view = View(timeout=300, disable_on_timeout=True)
            view.add_item(select_uid_pulldown(
                ctx, select_options, v.game_name))
            view.add_item(isPabricEnterButton(ctx))
            view.add_item(UidModalButton(ctx))
            await ctx.respond(embed=embed, view=view, ephemeral=True)
            print(
                f"==========\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nuidcontrole - 開く")
        except:
            view = View()
            button = UidModalButton(ctx)
            view.add_item(button)
            await ctx.respond(content="UIDが登録されていません。下のボタンから登録してください。", view=view, ephemeral=True)
            print(
                f"==========\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nuidcontrole - 登録してくれ")
            return


def setup(bot):
    bot.add_cog(uidListCog(bot))
