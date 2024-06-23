from lib.genshin_status_api import get_user_data, api_connect_generate_image, api_connect_profile_image
from enums.substatus import SubTypes
from enums.ImageTypeEnums import ImageTypeEnums
import discord
import view.genshin_view as genshin_view

class GenshinStatusModel():
    def __init__(
            self, 
            uid:int = 0, 
            nickname:str = "", 
            character_map:dict[str:int] = None, 
            user_data:dict = None, 
            image_file = None, 
            character_index:int = 0,
            profile_file = None,
            ) -> None:
        self, 
        self.uid = uid
        self.nickname = nickname
        self.character_map = character_map
        self.user_data = user_data
        self.score_type: SubTypes = SubTypes.ATK.value
        self.image_type: int = ImageTypeEnums.DEFAULT.value[0]
        self.image_file = image_file
        self.profile_file = profile_file
        self.character_index:int = character_index

    async def get_user(self, uid:int):
        response = await get_user_data(uid=uid)
        self.uid = int(response["uid"])
        self.nickname = str(response["nickname"])
        self.character_map = response["char_name_map"]
        self.user_data = response
        return self

    async def get_generate_image(self, chacacter_index:int):
        self.character_index = chacacter_index
        image_type = self.image_type
        data = self.user_data["characters"][chacacter_index]
        data["build_type"] = self.score_type
        self.image_file = await api_connect_generate_image(data, image_type)
        return self
    
    async def get_profile_image(self):
        self.profile_file = await api_connect_profile_image(self.user_data)
        return self

    def profile_to_discord(self):
        embed = discord.Embed(
            title=f"{self.nickname}",
            color=0x1e90ff,
        )

        embed.set_image(url=f"attachment://{str(self.uid)}.png")
        embed.set_footer(text="軽量化のため、最初の画像生成から約5分後に操作ができなくなります。ご了承ください。")
        return discord.File(self.profile_file, filename=str(self.uid)+'.png'), embed

    def set_build_type(self, build_type):
        self.image_type = build_type
        return self

    def set_score_type(self, score_type:SubTypes):
        self.score_type = score_type
        for i in self.user_data["characters"]:
            i["build_type"] = score_type
        return self

    def image_to_discord(self, character_index: int):
        embed = discord.Embed(
            title=f"{''.join([k for k, v in self.character_map.items() if v == character_index])}",
            color=0x1e90ff,
        )

        embed.set_image(url=f"attachment://{str(self.uid)}.png")
        embed.set_footer(text="軽量化のため、最初の画像生成から約5分後に操作ができなくなります。ご了承ください。")
        return discord.File(self.image_file, filename=str(self.uid)+'.png'), embed
    
    def is_character_map(self):
        return self.character_map != {}

    def is_character_list(self):
        return self.user_data["characters"] != []

    def get_character_button(self, view:discord.ui.View):
        names = []
        button_data = {}
        for k, v in self.character_map.items():
            names.append(k)
            button_data.update({k: str(v)})
            view.add_item(
                genshin_view.CharacterSelectButton(k, button_data, self))
        return view
    
    def get_status_image_view(self, user_id:int):
        view = discord.ui.View(timeout=300, disable_on_timeout=True)
        view.add_item(genshin_view.ScoreTypeSelecter(self))
        view.add_item(genshin_view.ImageTypeSelecter(self))
        view.add_item(genshin_view.GetProfileButton(uid=self.uid))
        view.add_item(genshin_view.DeleteButton(user_id=user_id))
        view = self.get_character_button(view=view)
        return view