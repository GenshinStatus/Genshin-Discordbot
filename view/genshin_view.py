import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks
from discord import Option, SlashCommandGroup
from enums.substatus import SubTypes
from enums.ImageTypeEnums import ImageTypeEnums
from model.user_data_model import GenshinStatusModel
from lib.log_output import log_output, log_output_interaction
from aiohttp import client_exceptions

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
        embed = ErrorEmbed(description=message)
        await interaction.edit_original_message(content=None, embed=embed, view=None)
        raise e
    except Exception as e:
        embed = ErrorEmbed(
            description='原因不明なエラーが発生しています。\n開発者に問い合わせください。')
        await interaction.edit_original_message(content=None, embed=embed)
        print(e)
        raise e
    return status

async def load_characters(status:GenshinStatusModel, interaction: discord.Interaction) -> GenshinStatusModel:
    if status.is_character_map():
        pass
    else:
        embed = ErrorEmbed(
            description="キャラクターのリストを取得できませんでした。\n原神の設定でプロフィールにキャラクターを掲載していないことが原因です。\nプロフィールにキャラクターを掲載してからもう一度お試しください。\n**データ更新にはしばらく時間がかかります。**")
        embed.set_image(
            url="https://genshin-cdn.cinnamon.works/notify/no_character_list.jpg")
        await interaction.edit_original_message(content=None, embed=embed, view=None)
        log_output_interaction(
            interaction=interaction, cmd="/genshinstat get 画像生成 未掲載エラー")
        raise
    if status.is_character_list():
        pass
    else:
        embed = ErrorEmbed(
            description="キャラクターのステータスを取得できませんでした。\n原神の設定でキャラクター詳細を非公開にしていることが原因です。\nキャラクター詳細を公開設定に変更してからもう一度お試しください。\n**データ更新にはしばらく時間がかかります。**")
        embed.set_image(url="attachment://character_status_error.png")
        file = discord.File("Image/character_status_error.png",
                            filename="character_status_error.png")
        await interaction.edit_original_message(content=None, embed=embed, view=None, file=file)
        log_output_interaction(
            interaction=interaction, cmd="/genshinstat get 画像生成 非公開エラー")
        raise
    return status

async def get_profile(uid, interaction: discord.Interaction):

    embed = LoadingEmbed(description='プロフィールをロード中...')
    await interaction.response.edit_message(content=None, embed=embed, view=None)
    status = GenshinStatusModel()
    try:
        status = await load_profile(status=status, uid=uid, interaction=interaction)
    except:
        return

    embed = LoadingEmbed(description='キャラクターラインナップをロード中...')
    await interaction.edit_original_message(content=None, embed=embed, view=None)
    status = await load_characters(status=status, interaction=interaction)

    embed = LoadingEmbed(description='画像を生成中...')
    await interaction.edit_original_message(content=None, embed=embed, view=None)
    status = await status.get_profile_image()
    data = status.profile_to_discord()
    view = View(timeout=300, disable_on_timeout=True)
    view = status.get_character_button(view=view)
    view.add_item(DeleteButton(user_id=interaction.user.id))
    await interaction.edit_original_message(content=None, view=view, embed=data[1], file=data[0])
    log_output_interaction(interaction=interaction,
                           cmd="/genshinstat get プロフィールロード完了")

# get_profileを実行するボタン
class GetProfileButton(discord.ui.Button):
    def __init__(self, uid: int, style=discord.ButtonStyle.green, label='プロフィール画像', **kwargs):
        self.uid = uid
        super().__init__(style=style, label=label, row=4, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        await get_profile(uid=self.uid, interaction=interaction)

class DeleteButton(discord.ui.Button):
    def __init__(self, user_id: int, style=discord.ButtonStyle.red, label='メッセージ削除', **kwargs):
        self.user_id = user_id
        super().__init__(style=style, label=label, row=4, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        if self.user_id == interaction.user.id:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(content="他人のメッセージは削除できません", ephemeral=True)

class ScoreTypeSelecter(discord.ui.Select):
    def __init__(self, status:GenshinStatusModel) -> None:
        super().__init__(placeholder="ビルドタイプを選択してください。")

        self.add_option(label="攻撃力基準",
                        value=SubTypes.ATK.value,
                        description='攻撃力% + 会心率×2 + 会心ダメージ',
                        emoji="<:ATTACK_PERCENT:971462863338213396>")
        self.add_option(label="元チャ効率基準",
                        value=SubTypes.CH.value,
                        description='元チャ効率% + 会心率×2 + 会心ダメージ',
                        emoji="<:CHARGE_EFFICIENCY:971462863229190154>")
        self.add_option(label="元チャ効率基準（Artifacter版計算式）",
                        value=SubTypes.CH2.value,
                        description='元チャ効率%×0.9 + 会心率×2 + 会心ダメージ',
                        emoji="<:CHARGE_EFFICIENCY:971462863229190154>")
        self.add_option(label="防御力基準",
                        value=SubTypes.DEF.value,
                        description='防御力% + 会心率×2 + 会心ダメージ',
                        emoji="<:DEFENSE_PERCENT:971462863250153502>")
        self.add_option(label=f"防御力基準（Artifacter版計算式）",
                        value=SubTypes.DEF2.value,
                        description='防御力%×0.8 + 会心率×2 + 会心ダメージ',
                        emoji="<:DEFENSE_PERCENT:971462863250153502>")
        self.add_option(label="HP基準",
                        value=SubTypes.HP.value,
                        description='HP% + 会心率×2 + 会心ダメージ',
                        emoji="<:HP_PERCENT:971462863334035466>")
        self.add_option(label="元素熟知基準",
                        value=SubTypes.EM.value,
                        description='（元素熟知 + 会心率×2 + 会心ダメージ）÷2',
                        emoji="<:ELEMENT_MASTERY:971462862948151358>")
        self.add_option(label="元素熟知基準（Artifacter版計算式）",
                        value=SubTypes.EM2.value,
                        description='元素熟知×0.25 + 会心率×2 + 会心ダメージ',
                        emoji="<:ELEMENT_MASTERY:971462862948151358>")
        self.status = status

    async def callback(self, interaction: discord.Interaction):
        self.status.set_score_type(self.values[0])
        embed = LoadingEmbed(description="画像を生成中")
        embed.set_image(url="attachment://Loading.gif")
        await interaction.response.edit_message(content=None, embed=embed, view=None, file=discord.File("Image/Loading.gif", filename='Loading.gif'))
        data = await self.status.get_generate_image(chacacter_index=self.status.character_index)
        data = data.image_to_discord(character_index=self.status.character_index)
        await interaction.edit_original_response(
            content=None,
            embed=data[1],
            file=data[0],
            view=self.status.get_status_image_view(user_id=interaction.user.id))


class ImageTypeSelecter(discord.ui.Select):
    def __init__(self, status:GenshinStatusModel) -> None:
        super().__init__(placeholder="画像生成タイプを選択してください。")

        self.add_option(label=ImageTypeEnums.DEFAULT.value[1],
                        value=str(ImageTypeEnums.DEFAULT.value[0]),
                        description='オリジナルデザインの画像生成です。キャラの見た目を重視しています。')
        self.add_option(label=ImageTypeEnums.ARTIFACTER.value[1],
                        value=str(ImageTypeEnums.ARTIFACTER.value[0]),
                        description='旧Artifacterデザインの画像生成です。聖遺物の見やすさを重視しています。')
        self.status = status

    async def callback(self, interaction: discord.Interaction):
        self.status.set_build_type(int(self.values[0]))
        embed = LoadingEmbed(description="画像を生成中")
        embed.set_image(url="attachment://Loading.gif")
        await interaction.response.edit_message(content=None, embed=embed, view=None, file=discord.File("Image/Loading.gif", filename='Loading.gif'))
        data = await self.status.get_generate_image(chacacter_index=self.status.character_index)
        data = data.image_to_discord(character_index=self.status.character_index)
        await interaction.edit_original_response(
            content=None,
            embed=data[1],
            file=data[0],
            view=self.status.get_status_image_view(user_id=interaction.user.id))


class CharacterSelectButton(discord.ui.Button):
    def __init__(self, label, button_data, status:GenshinStatusModel):
        super().__init__(style=discord.ButtonStyle.gray, label=label)
        self.button_data = button_data
        self.status = status

    async def callback(self, interaction: discord.Interaction):
        embed = LoadingEmbed(description="画像を生成中")
        embed.set_image(url="attachment://Loading.gif")
        await interaction.response.edit_message(content=None, embed=embed, view=None, file=discord.File("Image/Loading.gif", filename='Loading.gif'))
        data = await self.status.get_generate_image(chacacter_index=int(self.button_data[self.label]))
        data = data.image_to_discord(int(self.button_data[self.label]))
        await interaction.edit_original_response(
            content=None,
            embed=data[1],
            file=data[0],
            view=self.status.get_status_image_view(user_id=interaction.user.id))


class MyEmbed(discord.Embed):
    def __init__(self, color=0x1e90ff, title: str = None, url: str = None, description: str = None):
        super().__init__(color=color, title=title, url=url, description=description)


class LoadingEmbed(MyEmbed):
    def __init__(self, description: str):
        super().__init__(
            title='<a:loading:919603348049657936> ローディング中',
            description=description)


class ErrorEmbed(MyEmbed):
    def __init__(self, url: str = None, description: str = None):
        super().__init__(
            color=0xff0000,
            title=':warning: エラー',
            url=url,
            description=description)
