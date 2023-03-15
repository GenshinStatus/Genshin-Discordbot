import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks
from discord import Option, SlashCommandGroup
import aiohttp
from lib.yamlutil import yaml
import lib.picture as getPicture
from typing import List
import lib.sql as SQL
import cogs.uidlist as uidlist
import os
from lib.getCharacterStatus import CharacterStatus
from enums.substatus import SubTypes
from lib.gen_genshin_image import get_character_discord_file
from lib.log_output import log_output, log_output_interaction
from enums.ImageTypeEnums import ImageTypeEnums
import view.genshin_view as genshin_view
import lib.status_to_artifacter as status_to_artifacter
import lib.Generater as Artifacter_gen
from lib.log_exception import LogException

charactersYaml = yaml(path='characters.yaml')
characters = charactersYaml.load_yaml()
genshinJpYaml = yaml(path='genshinJp.yaml')
genshinJp = genshinJpYaml.load_yaml()


class GenshinUID():
    def __init__(self, uid: str) -> None:
        self.uid = uid
        self.data = None
        self.character_list = []
        self.score_type: SubTypes = SubTypes.ATTACK_PERCENT.value
        self.image_type: ImageTypeEnums = ImageTypeEnums.DEFAULT.value
        self.file = None
        self.discord_file = None
        self.button_data = None
        self.character_name = None

    def set_button_data(self, data, label):
        self.button_data = data
        self.character_name = label
        return self

    async def get_data(self):
        url = f"https://enka.network/api/uid/{self.uid}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 400:
                    raise FileNotFoundError
                if response.status != 200:
                    return None
                resp = await response.json()
        return resp

    def get_character_list(self):
        character_list = []
        for id in self.data["playerInfo"]["showAvatarInfoList"]:
            character_list.append(id["avatarId"])
        return character_list

    async def get_profile_discord_file(self):
        self.file = await getPicture.getProfile(self.uid, self.data)
        self.discord_file = discord.File(self.file, f"{self.uid}.png")
        return self

    def del_filepass(self):
        del self.discord_file
        os.remove(self.file)

    def get_profile_embed(self):
        try:
            embed = discord.Embed(
                title=f"{self.data['playerInfo']['nickname']}",
                color=0x1e90ff,
                description=f"uid: {self.uid}",
                url=f"https://enka.network/api/uid/{self.uid}"
            )
            embed.set_image(url=f"attachment://{self.uid}.png")
            return embed
        except:
            embed = discord.Embed(
                title=f"エラーが発生しました。APIを確認してからもう一度お試しください。\n{f'https://enka.network/api/uid/{self.uid}'}",
                color=0x1e90ff,
                url=f"https://enka.network/api/uid/{self.uid}"
            )
            return embed

    def get_status_image_view(self):
        view = View(timeout=300, disable_on_timeout=True)
        view.add_item(genshin_view.ScoreTypeSelecter(self))
        view.add_item(genshin_view.ImageTypeSelecter(self))
        view = self.get_character_button(view=view)
        return view

    def get_character_button(self, view):
        names = []
        button_data = {}
        for id in self.character_list:
            id = str(id)
            name = genshinJp[characters[str(id)]["NameId"]]
            names.append(name)
            button_data.update({name: id})
        # 名前をラベル、ついでにdictとuidも送り付ける
        for v in names:
            view.add_item(
                genshin_view.CharacterSelectButton(v, button_data, self))
        return view

    async def get_status_image(self, interaction: discord.Interaction, button_data, label):
        image_overwrite_file = discord.File(
            'Image/1x1.png', "image_overwrite_file.png")

        # ローディングメッセージ
        embed = genshin_view.LoadingEmbed(description='キャラクターをロード中...')
        await interaction.response.edit_message(content=None, embed=embed, view=None, file=image_overwrite_file)
        log_output_interaction(interaction=interaction,
                               cmd=f"genshinstat get キャラ取得 {self.uid} {button_data[label]}")

        # キャラクターのデータを取得します。
        json = await CharacterStatus.get_json(uid=self.uid)

        try:
            character_status = CharacterStatus.getCharacterStatus(
                json=json, id=button_data[label], build_type=self.score_type)
        except FileNotFoundError as e:
            embed = genshin_view.ErrorEmbed(
                description="キャラクターのステータスを取得できませんでした。\n原神の設定でキャラクター詳細を非公開にしていることが原因です。\nキャラクター詳細を公開設定に変更してからもう一度お試しください。")
            embed.set_image(url="attachment://character_status_error.png")
            file = discord.File("Image/character_status_error.png",
                                filename="character_status_error.png")
            log_output_interaction(
                interaction=interaction, cmd="/genshinstat get 画像生成 非公開エラー")
            return embed, file

        # ローディングメッセージ
        embed = genshin_view.LoadingEmbed(description='画像を生成中...')
        await interaction.edit_original_message(content=None, embed=embed, view=None)

        if self.image_type == "原神アーティファクター":
            try:
                file, url = Artifacter_gen.get_character_discord_file(
                    status_to_artifacter.get_artifacter_data(uid=self.uid, data=character_status))
            except Exception as e:
                embed = genshin_view.ErrorEmbed(
                    description="何らかの原因で画像生成ができませんでした。\nお手数をおかけしますが、```/genbot report```から報告をお願い致します。\n\n**※Artifacter版画像生成では一部の原神のデータを使用できない場合があります（一部の新武器や新キャラ等）。ご理解下さい。**")
                embed.set_image(url="attachment://generate_status_error.png")
                file = discord.File(
                    'Image/1x1.png', filename="generate_status_error.png")
                LogException(e)
                log_output_interaction(
                    interaction=interaction, cmd="/genshinstat get 画像生成 Artifacter エラー")
                return embed, file

        # 画像データを取得し、DiscordのFileオブジェクトとしてurlとfileを取得します。
        else:
            try:
                file, url = get_character_discord_file(
                    character_status=character_status, build_type=self.score_type
                )
            except Exception as e:
                embed = genshin_view.ErrorEmbed(
                    description="何らかの原因で画像生成ができませんでした。\nお手数をおかけしますが、```/genbot report```から報告をお願い致します。")
                embed.set_image(url="attachment://generate_status_error.png")
                file = discord.File(
                    'Image/1x1.png', filename="generate_status_error.png")
                LogException(e)
                log_output_interaction(
                    interaction=interaction, cmd="/genshinstat get 画像生成 Default エラー")
                return embed, file

        # 取得した画像でembed作成しれすぽんす
        embed = discord.Embed(
            title=f"{label}",
            color=0x1e90ff,
        )

        embed.set_image(url=url)
        embed.set_footer(text="軽量化のため、最初の画像生成から約5分後に操作ができなくなります。ご了承ください。")

        log_output_interaction(interaction=interaction,
                               cmd=f"/genshinstat get 画像生成 完了 {self.image_type} {self.score_type}")
        return embed, file
