from discord.ext import commands
from discord.ui import View, button, Button
from discord import Option, OptionChoice, SlashCommandGroup, Interaction
import discord
from model import quizmodel
from view.quiz import addquiz


class QuickPushQuiz(commands.Cog):
    def __init__(self, bot) -> None:
        print("init")
        self.bot = bot

    # quiz系コマンド
    _quiz_command = SlashCommandGroup(
        name="quiz",
        description="クイズ系のコマンドです",
    )

    _creation_quiz_command = _quiz_command.create_subgroup(
        name="creation",
        description="クイズの創作を行うグループです。"
    )

    _quiz_admin_command = SlashCommandGroup(
        name="quiz_admin",
        description="クイズを管理するためのコマンド群",
    )

    @_quiz_admin_command.command(
        name="set_channel",
        description="クイズをするためのチャンネルを設定します"
    )
    async def set_channel(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(discord.TextChannel, description="チャンネルの指定")
    ):
        channel: discord.TextChannel = ctx.channel if channel == None else channel
        quizmodel.set_quiz_channel(
            guild_id=ctx.guild_id,
            channel_id=channel.id,
        )

        await ctx.interaction.response.send_message(
            content=f"{channel.name}をクイズチャンネルに設定しました",
            ephemeral=True,
        )

    @_quiz_admin_command.command(
        name="remove_channel",
        description="クイズチャネルの登録を解除します"
    )
    async def remove_channel(
        self,
        ctx: discord.ApplicationContext,
    ):
        quizmodel.remove_quiz_channel(
            guild_id=ctx.guild_id,
        )

        await ctx.interaction.response.send_message(
            content=f"クイズチャンネルの登録を解除しました",
            ephemeral=True,
        )

    @_quiz_command.command(
        name="play",
        description="クイズを開始します"
    )
    async def play(
        self,
        ctx: discord.ApplicationContext,
        game: Option(int, description="繰り返し回数", min_value=1, max_value=10, default=3),
    ):
        # TODO: Classを用意してゲームを作る
        pass

    @_creation_quiz_command.command(
        name="add",
        description="クイズの追加処理を行います"
    )
    async def quiz_add(
        self,
        ctx: discord.ApplicationContext,
        quantity: Option(
            int,
            description="誤答の数",
            min_value=1,
            max_value=3,
            default=3
        )
    ):
        await ctx.response.send_modal(addquiz.AddQuizModal(quantity=quantity))


def setup(bot):
    bot.add_cog(QuickPushQuiz(bot=bot))
