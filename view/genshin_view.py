import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks
from discord import Option, SlashCommandGroup
from enums.substatus import SubTypes
from enums.ImageTypeEnums import ImageTypeEnums
from model.user_data_model import GenshinStatusModel


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
        await interaction.edit_original_message(
            content=None,
            embed=data[1],
            file=data[0],
            view=self.status.get_status_image_view())


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
        await interaction.edit_original_message(
            content=None,
            embed=data[1],
            file=data[0],
            view=self.status.get_status_image_view())


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
        await interaction.edit_original_message(
            content=None,
            embed=data[1],
            file=data[0],
            view=self.status.get_status_image_view())


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
