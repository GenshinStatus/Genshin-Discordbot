import discord


async def stop_message(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="⚠大事なお知らせ", color=0x1e90ff,
                          description=f"原神ステータスBotが認証され、ついに100サーバー以上で導入することが可能になりました。\n\nそれに伴い、暫定的に運用していた二代目以降のBotは**2023/2/1に停止する予定です。**\n\n以下のリンクから、初代原神ステータスBotの招待をお願い致します。\n\n**※UIDなどのユーザーデータはすべて引き継がれます。**\n\n")
    embed.add_field(
        name="招待リンク", value="https://discord.com/api/oauth2/authorize?client_id=1014120722404220998&permissions=414464854080&scope=bot%20applications.commands")
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1040527669420380160/1064407326297161768/image.png")
    await ctx.respond(embed=embed)
