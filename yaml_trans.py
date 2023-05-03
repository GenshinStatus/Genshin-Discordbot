from lib.sql import database

from lib.yamlutil import yaml

import discord

from datetime import datetime

# ややこしくなるのでコンバート終了後ファイルごと削除してください


def init(bot: discord.AutoShardedBot):
    channels: dict = yaml("channelId.yaml").load_yaml()

    for k, v in channels.items():
        database.table_update_sql(
            sql="""
            INSERT INTO notification_channel (guild_id, channel_id)
            VALUES (%s, %s)
            ON CONFLICT (guild_id)
            DO UPDATE SET channel_id = %s
            """,
            data=(k, v["channelid"],  v["channelid"]),
        )

    notifications: dict = yaml("notification.yaml").load_yaml()

    for k, v in notifications.items():

        database.table_update_sql(
            sql="""
            INSERT INTO genshin_notification (type_id, bot_id, user_id, guild_id, notification_time, plan_time)
            VALUES (%s, %s, %s, (select guild_id from notification_channel where channel_id = %s), %s, %s)
            """,
            data=(
                1,
                bot.user.id,
                int(v["userId"][2:-1]),
                v["channelId"],
                datetime.fromtimestamp(float(k)),
                datetime.fromtimestamp(float(v["time"])),
            ),
        )
