import discord
from discord.ui import Select, View
from discord.ext import commands, tasks
from discord.commands import Option, OptionChoice, SlashCommandGroup
import copy

mainOption = {
    "花": ["HP"],
    "羽": ["攻撃力"],
    "時計": ["HP%", "攻撃力%", "防御力%", "元素熟知", "元素チャージ効率"],
    "杯": ["HP%", "攻撃力%", "防御力%", "元素熟知", "元素ダメージ"],
    "冠": ["HP%", "攻撃力%", "防御力%", "元素熟知", "与える治癒効果", "会心率", "会心ダメージ"]
}

subOption = [
    "攻撃力",
    "攻撃力%",
    "防御力",
    "防御力%",
    "HP",
    "HP%",
    "元素熟知",
    "元素チャージ効率",
    "会心率",
    "会心ダメージ"
]

name = [
    "深林の記憶",
    "金メッキの夢",
    "辰砂往生録",
    "来歆の余響",
    "海染硨磲",
    "華館夢醒形骸記",
    "追憶のしめ縄",
    "絶縁の旗印",
    "蒼白の炎",
    "千岩牢固",
    "氷風を彷徨う勇士",
    "沈淪の心",
    "逆飛びの流星",
    "悠久の磐岩",
    "血染めの騎士道",
    "旧貴族のしつけ",
    "燃え盛る炎の魔女",
    "雷のような怒り",
    "翠緑の影",
    "剣闘士のフィナーレ",
    "愛される少女",
    "烈火を渡る賢者",
    "雷を鎮める尊者",
    "大地を流浪する楽団"
]

globalOption = ""

# 最初に出されるクラス。聖遺物のタイプを選択。


class ArtifactBaseSelectView(View):

    @discord.ui.select(
        placeholder="聖遺物タイプ",
        options=[
            discord.SelectOption(
                    label="花",
                    description="HP",),
            discord.SelectOption(
                label="羽",
                description="攻撃力",),
            discord.SelectOption(
                label="時計",
                description="、".join(mainOption["時計"])),
            discord.SelectOption(
                label="杯",
                description="、".join(mainOption["杯"])),
            discord.SelectOption(
                label="冠",
                description="、".join(mainOption["冠"])),
        ])
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        view = View()
        view.add_item(ArtifactSuboptionSelect(select.values[0]))
        await interaction.response.edit_message(content="サブオプションを選択してください", view=view)


#みかんさん感謝感激雨あられ - サブオプションを何とかする
class ArtifactSuboptionSelect(discord.ui.Select):
    def __init__(self, mainType: str):
        self.listSubOption: list[discord.SelectOption] = []
        self.mainType = mainType
        for v in subOption:
            self.listSubOption.append(discord.SelectOption(label=v))
        super().__init__(placeholder="サブオプションを選択（最大4つ）",
                         max_values=4, options=self.listSubOption)

    async def callback(self, interaction: discord.Interaction):
        resalt = []
        for n in self.values:
            resalt.append(n)
        await interaction.response.send_modal(ArtifactSuboptionValueModal(resalt, self.mainType))
        print(
            f"\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nartifact - サブオプション選択")


# 数値入力モーダル
class ArtifactSuboptionValueModal(discord.ui.Modal):
    def __init__(self, list: list, mainType: str):
        super().__init__(title="数値入力（半角数字で小数点まで入力してください）", timeout=300,)
        self.list = list
        self.mainType = mainType

        try:
            self.contentA = discord.ui.InputText(
                label=f"{self.list[0]}（半角数字で小数点まで入力してください）",
                style=discord.InputTextStyle.short,
                placeholder=f"{self.list[0]}の数値",
                required=True,
            )
            self.add_item(self.contentA)
        except:
            print(":)")
        try:
            self.contentB = discord.ui.InputText(
                label=f"{self.list[1]}（半角数字で小数点まで入力してください）",
                style=discord.InputTextStyle.short,
                placeholder=f"{self.list[1]}の数値",
                required=True,
            )
            self.add_item(self.contentB)
        except:
            print(":)")
        try:
            self.contentC = discord.ui.InputText(
                label=f"{self.list[2]}（半角数字で小数点まで入力してください）",
                style=discord.InputTextStyle.short,
                placeholder=f"{self.list[2]}の数値",
                required=True,
            )
            self.add_item(self.contentC)
        except:
            print(":)")
        try:
            self.contentD = discord.ui.InputText(
                label=f"{self.list[3]}（半角数字で小数点まで入力してください）",
                style=discord.InputTextStyle.short,
                placeholder=f"{self.list[3]}の数値",
                required=True,
            )
            self.add_item(self.contentD)
        except:
            print(":)")

    async def callback(self, interaction: discord.Interaction) -> None:
        resalt = {}
        try:
            resalt[self.list[0]] = self.contentA.value
        except:
            print(":)")
        try:
            resalt[self.list[1]] = self.contentB.value
        except:
            print(":)")
        try:
            resalt[self.list[2]] = self.contentC.value
        except:
            print(":)")
        try:
            resalt[self.list[3]] = self.contentD.value
        except:
            print(":)")
        view = View()
        view.add_item(ArtifactScoreSelectView(resalt, self.mainType))
        await interaction.response.edit_message(content="スコア計算方法", view=view)


# スコア計算方法を選択
class ArtifactScoreSelectView(discord.ui.Select):

    def __init__(self, resaltDict: dict, mainType: str):
        self.listScoreOption: list[discord.SelectOption] = []
        self.mainType = mainType
        self.subDict = resaltDict
        self.listScoreOption.append(
            discord.SelectOption(
                label="会心ビルド",
                description="攻撃力%+会心率×2+会心ダメージ")
        )
        self.listScoreOption.append(
            discord.SelectOption(
                label="HPビルド",
                description="HP%+会心率×2+会心ダメージ")
        )
        self.listScoreOption.append(
            discord.SelectOption(
                label="防御力ビルド",
                description="防御力%+会心率×2+会心ダメージ")
        )
        self.listScoreOption.append(
            discord.SelectOption(
                label="元素チャージビルド",
                description="元素チャージ効率+会心率×2+会心ダメージ")
        )
        self.listScoreOption.append(
            discord.SelectOption(
                label="元素熟知ビルド",
                description="(元素熟知+会心率×2+会心ダメージ)÷2")
        )
        super().__init__(placeholder="スコア計算方法を選択", options=self.listScoreOption)

    async def callback(self, interaction: discord.Interaction):
        try:
            attack = 0
            rate = 0
            damage = 0
            hp = 0
            defence = 0
            cherge = 0
            mastery = 0
            if self.values[0] == "会心ビルド":
                for k, v in self.subDict.items():
                    if k == "攻撃力%":
                        attack = v
                    elif k == "会心率":
                        rate = v
                    elif k == "会心ダメージ":
                        damage = v
                resalt = float(attack) + float(rate)*2 + float(damage)
            elif self.values[0] == "HPビルド":
                for k, v in self.subDict.items():
                    if k == "HP%":
                        hp = v
                    elif k == "会心率":
                        rate = v
                    elif k == "会心ダメージ":
                        damage = v
                resalt = float(hp) + float(rate)*2 + float(damage)
            elif self.values[0] == "防御力ビルド":
                for k, v in self.subDict.items():
                    if k == "防御力%":
                        defence = v
                    elif k == "会心率":
                        rate = v
                    elif k == "会心ダメージ":
                        damage = v
                resalt = float(defence) + float(rate)*2 + float(damage)
            elif self.values[0] == "元素チャージビルド":
                for k, v in self.subDict.items():
                    if k == "元素チャージ効率":
                        cherge = v
                    elif k == "会心率":
                        rate = v
                    elif k == "会心ダメージ":
                        damage = v
                resalt = float(cherge) + float(rate)*2 + float(damage)
            elif self.values[0] == "元素熟知ビルド":
                for k, v in self.subDict.items():
                    if k == "元素熟知":
                        mastery = v
                    elif k == "会心率":
                        rate = v
                    elif k == "会心ダメージ":
                        damage = v
                resalt = float(mastery) + float(rate)*2 + float(damage)
                resalt /= 2
        except:
            await interaction.response.edit_message(content="エラー：入力された数値が正しくない数値だった可能性があります。数値は半角英数字で小数点第一位まで記入してください。", view=None, embed=None)
            print(
                f"\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nartifact_detail - エラー表示")
            print(self.subDict)
            return
        print(str(round(resalt, 1)))
        embed = discord.Embed(title="聖遺物スコア計算結果", color=0x1e90ff,
                              description=str(round(resalt, 1)))
        # view=View()
        #view.add_item(isPicture(score=str(round(resalt, 1)), subDict=self.subDict, mainType=self.mainType))
        # await interaction.response.edit_message(content=str(round(resalt, 1)),view=view)
        await interaction.response.edit_message(content=None, view=None, embed=embed)
        print(
            f"\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nartifact_detail - 結果表示")


class isPicture(discord.ui.Button):
    def __init__(self, score: str, subDict: dict, mainType: str):
        self.score = score
        self.subDict = subDict
        self.mainType = mainType
        self.mainOption = copy.copy(mainOption[mainType])
        for k, v in self.subDict.items():
            try:
                self.mainOption.remove(k)
            except:
                continue
        super().__init__(style=discord.ButtonStyle.green, label="画像化する")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="メインオプションを選択", view=MainOptionButtons(self.mainOption, self.score, self.subDict, self.mainType))


# 選択されたタイプから予想されるメインオプションが入ったリストを回してボタンにする
class MainOptionButtons(View):
    def __init__(self, data: list, score: str, subDict: dict, mainType: str):
        self.score = score
        self.subDict = subDict
        self.mainType = mainType
        super().__init__(timeout=300, disable_on_timeout=True)
        for v in data:
            self.add_item(isMainOptionButton(
                v, self.score, self.subDict, self.mainType))

# ボタンにされたメインオプション。選択されたボタンのラベルをサブオプション選択クラスに送る


class isMainOptionButton(discord.ui.Button):
    def __init__(self, mainOption: str, score: str, subDict: dict, mainType: str):
        super().__init__(style=discord.ButtonStyle.secondary, label=mainOption)
        self.mainOption = mainOption
        self.score = score
        self.subDict = subDict
        self.mainType = mainType

    async def callback(self, interaction: discord.Interaction):
        global globalOption
        globalOption = self.label
        await interaction.response.send_modal(mainOptionValueModal(self.label, self.score, self.subDict, self.mainType))
        print(
            f"\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nartifact - メインオプション数値入力")


# メインオプション数値入力モーダル
class mainOptionValueModal(discord.ui.Modal):
    def __init__(self, mainOption: str, score: str, subDict: dict, mainType: str):
        super().__init__(title="メインオプション数値入力", timeout=300,)
        self.mainOption = mainOption
        self.score = score
        self.subDict = subDict
        self.mainType = mainType

        self.mainOptionValue = discord.ui.InputText(
            label="メインオプションの数値",
            style=discord.InputTextStyle.short,
            required=True,
        )
        self.add_item(self.mainOptionValue)

    async def callback(self, interaction: discord.Interaction) -> None:
        self.mainOptionValue = self.mainOptionValue.value
        view = View()
        view.add_item(ArtifactNameSelect(self.mainOptionValue,
                      self.mainOption, self.score, self.subDict, self.mainType))
        await interaction.response.edit_message(content=f"聖遺物の名前を選んで下さい", view=view)
        return


#みかんさん感謝感激雨あられ - 聖遺物の名前を何とかする
class ArtifactNameSelect(discord.ui.Select):
    def __init__(self, mainOptionValue: str, mainOption: str, score: str, subDict: dict, mainType: str):
        self.listName: list[discord.SelectOption] = []
        self.mainOptionValue = mainOptionValue
        self.mainOption = mainOption
        self.score = score
        self.subDict = subDict
        self.mainType = mainType

        for v in name:
            self.listName.append(discord.SelectOption(label=v))
        super().__init__(placeholder="聖遺物セット名を選択", options=self.listName)

    async def callback(self, interaction: discord.Interaction):
        print(self.values[0])
        resalt = []
        for n in self.values:
            resalt.append(n)
        await interaction.response.send_modal(ArtifactSuboptionValueModal(resalt, self.mainType))
        print(
            f"\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\nartifact - サブオプション選択")


class ArtifactCog(commands.Cog):

    def __init__(self, bot):
        print('genbot_initしたよ')
        self.bot = bot

    artifact = SlashCommandGroup('artifact', 'test')

    @artifact.command(name='get_detail', description='より詳細に聖遺物スコアを計算します。')
    async def get_detail(self, ctx: discord.ApplicationContext,):
        await ctx.respond(content="聖遺物のタイプを選んでね", view=ArtifactBaseSelectView(), ephemeral=True)
        print(
            f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nartifact_detail - コマンド使用")

    @artifact.command(name='get', description='手軽に聖遺物スコアを計算します。')
    async def get(
        self,
        ctx: discord.ApplicationContext,
        damage: Option(float, required=False,
                       description="攻撃力%"),
        crper: Option(float, required=False,
                      description="会心率"),
        crdamage: Option(float, required=False,
                         description="会心ダメージ")
    ):
        if damage == None:
            damage = 0
        if crper == None:
            crper = 0
        if crdamage == None:
            crdamage = 0
        try:
            resalt = float(damage) + float(crper)*2 + float(crdamage)
        except:
            await ctx.respond(content="有効な数値を入力してください", ephemeral=True)
            print(
                f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nartifact_get - エラー表示")
            print(damage)
            print(crper)
            print(crdamage)
            return
        embed = discord.Embed(title="会心基準聖遺物スコア計算結果", color=0x1e90ff,
                              description=str(round(resalt, 1)))
        embed.set_footer(
            text="HP基準計算など、他の計算方式を使う場合はは /artifact get_detail からやってね")
        await ctx.respond(embed=embed, ephemeral=True)
        print(
            f"\n実行者:{ctx.user.name}\n鯖名:{ctx.guild.name}\nartifact_get - 結果表示")


def setup(bot):
    bot.add_cog(ArtifactCog(bot))
