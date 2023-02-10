from discord.ui import View, Select, Button, Modal, InputText
from discord.ext import pages
from discord import Embed, Color, EmbedField, Interaction, SelectOption, ButtonStyle, InputTextStyle
from model import quizmodel


class AddingConfirmationEmbed(Embed):
    def __init__(self, description: str, fields: list[EmbedField]):
        super().__init__(
            color=Color.blue,
            title="追加された問題の確認",
            description=description,
            fields=fields
        )


class AddQuizModal(Modal):
    def __init__(self, quantity: int, image_url: str) -> None:
        self.image_url = image_url
        super().__init__(title="あなたの考えた問題を入力してください！")
        self.add_item(
            InputText(
                label="問題の文章",
                style=InputTextStyle.long,
                max_length=2000,
                required=True,
            )
        )
        self.add_item(
            InputText(
                label="正解の回答",
                style=InputTextStyle.short,
                max_length=30,
                required=True,
            )
        )
        for i in range(1, quantity+1):
            self.add_item(
                InputText(
                    label=f"{i}つ目の誤答",
                    style=InputTextStyle.short,
                    max_length=30,
                    required=True,
                )
            )

    async def callback(self, interaction: Interaction):
        quiz_data = self.children[0].value
        answer = self.children[1].value

        quizmodel.QuizData(
            quiz_data=quiz_data,
            ansewr=answer
        )
