import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks
from discord import Option, SlashCommandGroup
from enums.substatus import SubTypes
from enums.ImageTypeEnums import ImageTypeEnums


class ScoreTypeSelecter(discord.ui.Select):
    def __init__(self, status) -> None:
        super().__init__(placeholder="ビルドタイプを選択してください。")

        self.add_option(label=SubTypes.ATTACK_PERCENT.value,
                        value=SubTypes.ATTACK_PERCENT.value,
                        description='攻撃力% + 会心率×2 + 会心ダメージ')
        self.add_option(label=SubTypes.CHARGE_EFFICIENCY.value,
                        value=SubTypes.CHARGE_EFFICIENCY.value,
                        description='元チャ効率% + 会心率×2 + 会心ダメージ')
        self.add_option(label=SubTypes.DEFENSE_PERCENT.value,
                        value=SubTypes.DEFENSE_PERCENT.value,
                        description='防御力% + 会心率×2 + 会心ダメージ')
        self.add_option(label=SubTypes.HP_PERCENT.value,
                        value=SubTypes.HP_PERCENT.value,
                        description='HP% + 会心率×2 + 会心ダメージ')
        self.add_option(label=SubTypes.ELEMENT_MASTERY.value,
                        value=SubTypes.ELEMENT_MASTERY.value,
                        description='（元素熟知 + 会心率×2 + 会心ダメージ）÷2')
        self.status = status

    async def callback(self, interaction: discord.Interaction):
        self.status.score_type = self.values[0]
        data = await self.status.get_status_image(
            interaction=interaction, button_data=self.status.button_data, label=self.status.character_name)
        await interaction.edit_original_message(
            content=None,
            embed=data[0],
            file=data[1],
            view=self.status.get_status_image_view())


class ImageTypeSelecter(discord.ui.Select):
    def __init__(self, status) -> None:
        super().__init__(placeholder="画像生成タイプを選択してください。")

        self.add_option(label=ImageTypeEnums.DEFAULT.value,
                        value=ImageTypeEnums.DEFAULT.value,
                        description='オリジナルの画像生成。常に最新のデータが使用されます。')
        self.add_option(label=ImageTypeEnums.ARTIFACTER.value,
                        value=ImageTypeEnums.ARTIFACTER.value,
                        description='旧Artifacterの画像生成。最新のキャラは生成できません。')
        self.status = status

    async def callback(self, interaction: discord.Interaction):
        self.status.image_type = self.values[0]
        data = await self.status.get_status_image(
            interaction=interaction, button_data=self.status.button_data, label=self.status.character_name)
        await interaction.edit_original_message(
            content=None,
            embed=data[0],
            file=data[1],
            view=self.status.get_status_image_view())


class CharacterSelectButton(discord.ui.Button):
    def __init__(self, label, button_data, status):
        super().__init__(style=discord.ButtonStyle.gray, label=label)
        self.button_data = button_data
        self.status = status

    async def callback(self, interaction: discord.Interaction):
        self.status = self.status.set_button_data(self.button_data, self.label)
        data = await self.status.get_status_image(
            interaction=interaction, button_data=self.status.button_data, label=self.status.character_name)
        await interaction.edit_original_message(
            content=None,
            embed=data[0],
            file=data[1],
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
