import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks
from discord import Option, SlashCommandGroup
import lib.sql as SQL
import cogs.uidlist as uidlist
from lib.log_output import log_output, log_output_interaction
import view.genshin_view as genshin_view
from model.user_data_model import GenshinStatusModel

MESSAGES = {
    500: "サーバーで未知のエラーが発生しました。\nアップデートの影響により、新キャラクターや新武器等にまだ対応していないものが含まれている可能性があります。\nサポートサーバーをご確認ください。",
    435: "UIDのフォーマットが間違っています。\n半角数字で入力してください。",
    436: "入力されたものが存在するUIDではありません。\nもう一度確認してやり直してください。",
    437: "ゲームメンテナンスやアップデートの影響により\nEnka.network（ビルドデータを取得するサービス）が停止している状態です。\nしばらくお待ちください。\n※Bot運営チームはこれについて確認ぐらいしか取れないです。\n詳しくはEnkaのTwitterを確認してください。\nhttps://twitter.com/EnkaNetwork",
    438: "処理が追いついていません。\nしばらくしても解決しない場合は、開発者に対してコンタクトをとってください。",
    439: "Enka.network（ビルドデータを取得するサービス）のサーバーにエラーが発生しています。\n詳しくはEnkaのTwitterを確認してください。\nhttps://twitter.com/EnkaNetwork",
    440: "Enka.network（ビルドデータを取得するサービス）サーバーの一時停止中です。\nしばらくお待ちください。\n※開発者はこれについて確認ぐらいしか取れないです。\n詳しくはEnkaのTwitterを確認してください。\nhttps://twitter.com/EnkaNetwork",
    441: "Enka.network（ビルドデータを取得するサービス）のサーバーに原因不明のエラーが発生しています。\nしばらくお待ちください。\n※原神ステータスBotの運営チームはこれについて確認ぐらいしか取れないです。\n詳しくはEnkaNetworkのTwitterを確認してください。\nhttps://twitter.com/EnkaNetwork"
}

async def load_profile(status:GenshinStatusModel, uid, interaction: discord.Interaction) -> GenshinStatusModel:
    try:
        await status.get_user(uid=int(uid))
    except client_exceptions.ClientResponseError as e:
        message = f"エラーが発生しました。\n\
            しばらく時間をおいてからもう一度お試しください。\n\
            原因が解決しない場合は、開発者に問い合わせください。\n\n\
            **エラー詳細：**\
            ```{MESSAGES[e.status]}```\n\n\
            **問い合わせる前にサポートサーバーで最新情報を確認してください。**\n\
            https://discord.gg/MxZNQY9CyW\
        "
        embed = genshin_view.ErrorEmbed(description=message)
        await interaction.edit_original_response(content=None, embed=embed, view=None)
        raise e
    except Exception as e:
        embed = genshin_view.ErrorEmbed(
            description='原因不明なエラーが発生しています。\n開発者に問い合わせください。')
        await interaction.edit_original_response(content=None, embed=embed)
        print(e)
        raise e
    return status

async def load_characters(status:GenshinStatusModel, interaction: discord.Interaction) -> GenshinStatusModel:
    if status.is_character_map():
        pass
    else:
        embed = genshin_view.ErrorEmbed(
            description="キャラクターのリストを取得できませんでした。\n原神の設定でプロフィールにキャラクターを掲載していないことが原因です。\nプロフィールにキャラクターを掲載してからもう一度お試しください。\n**データ更新にはしばらく時間がかかります。**")
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1069630896367480962/1069631267873751051/image.png")
        await interaction.edit_original_response(content=None, embed=embed, view=None)
        log_output_interaction(
            interaction=interaction, cmd="/genshinstat get 画像生成 未掲載エラー")
        raise
    if status.is_character_list():
        pass
    else:
        embed = genshin_view.ErrorEmbed(
            description="キャラクターのステータスを取得できませんでした。\n原神の設定でキャラクター詳細を非公開にしていることが原因です。\nキャラクター詳細を公開設定に変更してからもう一度お試しください。\n**データ更新にはしばらく時間がかかります。**")
        embed.set_image(url="attachment://character_status_error.png")
        file = discord.File("Image/character_status_error.png",
                            filename="character_status_error.png")
        await interaction.edit_original_response(content=None, embed=embed, view=None, file=file)
        log_output_interaction(
            interaction=interaction, cmd="/genshinstat get 画像生成 非公開エラー")
        raise
    return status
    
async def get_profile(uid, interaction: discord.Interaction):

    embed = genshin_view.LoadingEmbed(description='プロフィールをロード中...')
    await interaction.response.edit_message(content=None, embed=embed, view=None)
    status = GenshinStatusModel()
    try:
        status = await load_profile(status=status, uid=uid, interaction=interaction)
    except:
        return

    embed = genshin_view.LoadingEmbed(description='キャラクターラインナップをロード中...')
    await interaction.edit_original_response(content=None, embed=embed, view=None)
    status = await load_characters(status=status, interaction=interaction)

    embed = genshin_view.LoadingEmbed(description='画像を生成中...')
    await interaction.edit_original_response(content=None, embed=embed, view=None)
    status = await status.get_profile_image()
    data = status.profile_to_discord()
    view = View(timeout=300, disable_on_timeout=True)
    view = status.get_character_button(view=view)
    await interaction.edit_original_response(content=None, view=view, embed=data[1], file=data[0])
    log_output_interaction(interaction=interaction,
                           cmd="/genshinstat get プロフィールロード完了")

class UidModal(discord.ui.Modal):  # UIDを聞くモーダル
    def __init__(self):
        super().__init__(title="UIDを入力してください。", timeout=300,)

        self.uid = discord.ui.InputText(
            label="UID",
            style=discord.InputTextStyle.short,
            min_length=9,
            max_length=10,
            placeholder="000000000",
            required=True,
        )
        self.add_item(self.uid)

    async def callback(self, interaction: discord.Interaction) -> None:
        await genshin_view.get_profile(self.uid.value, interaction)


class UidModalButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="登録せずにUIDから検索", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UidModal())


class UidButton(discord.ui.Button):
    def __init__(self, uid):
        super().__init__(label="登録されたUIDを使う", style=discord.ButtonStyle.green)
        self.uid = uid

    async def callback(self, interaction: discord.Interaction):
        await genshin_view.get_profile(self.uid, interaction)


class select_uid_pulldown(discord.ui.Select):
    def __init__(self, selectOptions: list[discord.SelectOption], game_name):
        super().__init__(placeholder="表示するUIDを選択してください", options=selectOptions)
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        await genshin_view.get_profile(self.values[0], interaction)


class GenshinCog(commands.Cog):

    def __init__(self, bot):
        print('genshin初期化')
        self.bot = bot

    genshin = SlashCommandGroup('genshinstat', 'test')

    @commands.slash_command(name="status", description="UIDからキャラ情報を取得し、画像を生成します")
    async def status_command(
            self,
            ctx: discord.ApplicationContext
    ):
        await GenshinCog.input_uid(self, ctx)

    @genshin.command(name="get", description="UIDからキャラ情報を取得し、画像を生成します")
    async def genshin_get(
            self,
            ctx: discord.ApplicationContext,
    ):
        await GenshinCog.input_uid(self, ctx)

    async def input_uid(self, ctx):
        view = View(timeout=300, disable_on_timeout=True)
        select_options: list[discord.SelectOption] = []
        userData = SQL.User.get_user_list(ctx.author.id)

        #  登録してないときの処理
        if userData == []:
            view.add_item(uidlist.UidModalButton(ctx))
            view.add_item(UidModalButton())
            embed = genshin_view.MyEmbed(
                title='UID選択', description='UIDが登録されていません。下のボタンから登録すると、UIDをいちいち入力する必要がないので便利です。\n下のボタンから、登録せずに確認できます。')
            await ctx.respond(content=None,
                              embed=embed,
                              view=view, 
                              ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
            log_output(ctx=ctx, cmd="/genshinstat get 未登録")
            return

        #  1つだけ登録してたときの処理
        if len(userData) == 1:
            view.add_item(UidButton(userData[0].uid))
            view.add_item(UidModalButton())
            embed = genshin_view.MyEmbed(
                title='UID選択', description='UIDが登録されています。登録されているUIDを使うか、直接UIDを指定するか選んでください。')
            await ctx.respond(content=None, embed=embed, view=view, ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
            log_output(ctx=ctx, cmd="/genshinstat get 登録済")
            return

        #  それ以外
        for v in userData:
            select_options.append(
                discord.SelectOption(label=v.game_name, description=str(v.uid), value=str(v.uid)))
        view.add_item(select_uid_pulldown(select_options, v.game_name))
        view.add_item(UidModalButton())
        embed = genshin_view.MyEmbed(
            title='UID選択', description='UIDが複数登録されています。表示するUIDを選ぶか、ボタンから指定してください。')
        await ctx.respond(content=None, embed=embed, view=view, ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
        log_output(ctx=ctx, cmd="/genshinstat get 複数登録済")
        return


def setup(bot):
    bot.add_cog(GenshinCog(bot))
