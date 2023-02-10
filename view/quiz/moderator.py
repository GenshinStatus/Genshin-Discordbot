from discord.ui import View, Select, Button
from discord.ext import pages
from discord import Embed, Color, EmbedField, Interaction, SelectOption, ButtonStyle
from model import quizmodel
import math


class QuizEmbed(Embed):
    """クイズの詳細表示をするためのEmbed

    Args:
        Embed (Embed): discrodに定義されたEmbed
    """

    def __init__(
        self,
        title: str,
        description: str,
        fields: list[EmbedField],
        image_url: str = None,

    ) -> None:
        """クイズの詳細を記述するためのEmbedです

        Args:
            title (str): クイズのタイトル
            description (str): 問題文
            fields (list[EmbedField]): 回答一覧
            image_url (str, optional): 画像URL. Defaults to None.
        """
        super().__init__(
            color=Color.greyple(),
            title=title,
            description=description,
            fields=fields,
        )
        if image_url is not None:
            self.set_image(url=image_url)


class QuizListEmbed(Embed):
    def __init__(
        self,
        title_type: str,
        description: str,
        fields: list[EmbedField]
    ):
        """クイズ一覧を表示するEmbed

        Args:
            title_type (str): 未認証など
            description (str): 説明
            fields (list[EmbedField]): 問題のタイトルなど
        """
        super().__init__(
            color=Color.blurple(),
            title=f"{title_type}一覧",
            description=description,
            fields=fields,
        )


class QuizListView(View):
    def __init__(self, options: list[SelectOption]):
        super().__init__()
        # self.tmp_embed = tmp_embed
        self.add_item(QuizListSelect(options=options))


# class BackButton(Button):
#     def __init__(self, style: ButtonStyle = ButtonStyle.red,):
#         super().__init__(style=style, label="戻る", custom_id="back", row=3)

#     async def callback(self, interaction: Interaction):
#         view: QuizListView = self.view
#         view.remove_item(view.get_item("back"))
#         view.remove_item(view.get_item("active"))
#         await interaction.response.edit_message(view=view, embed=view.tmp_embed)


class ActiveButton(Button):
    def __init__(self, quiz_id: int):
        super().__init__(style=ButtonStyle.green, label="有効化", custom_id="active", row=3, )
        self.quiz_id = quiz_id

    async def callback(self, interaction: Interaction):
        user_id = interaction.user.id
        quiz_id = self.quiz_id
        quizmodel.global_quiz_activation(quiz_id=quiz_id, user_id=user_id)
        print("有効化")
        pagenator = get_quiz_list_paginator()

        await pagenator.respond(interaction=interaction, ephemeral=True)


class QuizListSelect(Select):
    def __init__(self, options: list[SelectOption]) -> None:
        super().__init__(placeholder="選択してください。", options=options)

    async def callback(self, interaction: Interaction):
        quiz_id = int(self.values[0])
        quiz = quizmodel.get_quiz(quiz_id=quiz_id)
        fields = [
            EmbedField(
                name=quiz.ansewr,
                value="正解の答え",
                inline=False,
            )
        ]
        for i, v in enumerate(quiz.options):
            fields.append(
                EmbedField(
                    name=v,
                    value=f"不正解の答え {i + 1}",
                    inline=False,
                )
            )
        embed = QuizEmbed(
            title=quiz.quiz_data,
            description=quiz.quiz_data,
            fields=fields,
            image_url=quiz.image_url,
        )
        view: QuizListView = self.view
        if view.get_item("active") is None:
            view.add_item(ActiveButton(quiz_id=quiz_id))
            # view.add_item(BackButton())
        await interaction.response.edit_message(embed=embed, view=self.view)


def __get_quiz_list_pages() -> pages.Page:
    row = 10
    quiz_list = quizmodel.global_quiz_list()
    quiz_length = len(quiz_list)

    quiz_pages: list[pages.Page] = []
    for i in range(math.ceil(quiz_length/row)):
        last_page = (i+1)*row
        last_page = last_page if last_page < quiz_length else quiz_length
        tmp_list = quiz_list[i*row: last_page]
        embed = QuizListEmbed(
            title_type="未認証",
            description="現在未認証状態のクイズの一覧です。",
            fields=[
                EmbedField(
                    name=quiz.quiz_data,
                    value=f"画像あり: {quiz.image_url != None}",
                    inline=False,
                ) for quiz in tmp_list
            ]
        )
        quiz_pages.append(
            pages.Page(
                embeds=[embed],
                custom_view=QuizListView(
                    options=[
                        SelectOption(
                            label=f"{quiz.quiz_id}:{quiz.quiz_data}",
                            value=str(quiz.quiz_id)
                        )
                        for quiz in tmp_list
                    ],
                    # tmp_embed=embed,
                )
            )
        )
    return quiz_pages


def get_quiz_list_paginator() -> pages.Paginator:
    paginator = pages.Paginator(
        pages=__get_quiz_list_pages(),
        disable_on_timeout=True,
        timeout=300,
        default_button_row=4
    )
    return paginator
