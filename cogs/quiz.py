from discord.ext import commands
from discord.ui import View, button, Button
from discord import Option, OptionChoice, SlashCommandGroup, Interaction
import discord
from model import quizmodel


class QuickPushQuiz(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    # quiz系コマンド
    _quiz_command = SlashCommandGroup(
        name="quiz",
        description="クイズ系のコマンドです",
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
