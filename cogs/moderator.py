from discord.ext import commands
from discord import SlashCommandGroup
import discord
import os

# 環境変数にクイズなどの登録が可能なモデレーターが存在できるギルドを定義しておきます
GUILDS = os.getenv("MODERAOR_GUILDS")
MODERAOR_ROLE = int(os.getenv("MODERAOR_ROLE"))


class Moderaor(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    # quiz系コマンド
    _moderaor_command = SlashCommandGroup(
        name="moderaor",
        description="BOT管理者系のコマンドです。一部のユーザー以外にこのコマンドは許可されません。",
        guild_ids=[int(guild) for guild in GUILDS.split(",")],
        guild_only=True,
        checks=[commands.has_role(MODERAOR_ROLE).predicate],
    )

    @_moderaor_command.command(
        name="quiz_review",
        description="クイズを審査し公開するかの指定をします。"
    )
    async def quiz_review(
        self,
        ctx: discord.ApplicationContext,
    ):
        test = ctx.user.get_role(MODERAOR_ROLE) != None

        if test != None:
            print("もってる")
        else:
            print("もってない")

        await ctx.response.send_message(f"ロールの判定が動作してるかを確認: {test}")

        # TODO: Classを用意してゲームを作る
        pass

def setup(bot):
    bot.add_cog(Moderaor(bot))
