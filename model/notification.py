from lib.sql import database
from typing import Tuple
from datetime import datetime


class Notification:
    """通知に関する構造体クラス
    """

    def __init__(self, notification_id: int, type_id: int, type_name: str, bot_id: int, user_id: int, guild_id: int, notification_time: datetime, plan_time: datetime):
        self.notification_id = notification_id
        self.type_id = type_id
        self.type_name = type_name
        self.bot_id = bot_id
        self.user_id = user_id
        self.guild_id = guild_id
        self.notification_time = notification_time
        self.plan_time = plan_time


def user_notifications_search(guild_id: int, user_id: int, bot_id: int) -> list[Notification]:
    """ユーザーの要望で自身の通知予約をチェックする

    Args:
        guild_id (int): ギルドのID
        user_id (int): ユーザーのID
        bot_id (int): BOTのID

    Returns:
        list[Notification]: 通知リスト
    """
    result: Tuple = database.load_data_sql(
        sql="""
            select notification_id, type_id, type_name, bot_id, user_id, guild_id, notification_time, plan_time
            from genshin_notification
            left join notification_type using(type_id)
            where guild_id =%s
            and user_id =%s
            and bot_id =%s
            """,
        data=(guild_id, user_id, bot_id),
    )
    return [Notification(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]) for v in result]


def executing_notifications_search(bot_id: int) -> Tuple[list[Notification], dict[int, int]]:
    """通知を実行する対象を検索する

    Args:
        bot_id (int): BOTのID

    Returns:
        list[Notification]: 通知リスト
        dict[int, int]: ギルドIDに足しての通知チャンネル
    """
    result: Tuple = database.load_data_sql(
        sql="""
            select notification_id, type_id, type_name, bot_id, user_id, guild_id, notification_time, plan_time
            from genshin_notification
            left join notification_type using(type_id)
            where notification_time <= %s
            and bot_id = %s
            """,
        data=(datetime.now(), bot_id),
    )
    obj = [Notification(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7])
           for v in result]

    if len(obj) == 0:
        raise ValueError("Not found notification")

    col_size = ",".join(["%s"] * len(result))

    result: Tuple = database.load_data_sql(
        sql=f"""
        select guild_id, channel_id from notification_channel where guild_id in({col_size})
        """,
        data=tuple((v.guild_id for v in obj))
    )
    obj2 = {v[0]: v[1] for v in result}

    return obj, obj2


def delete_notifications(notification_ids: tuple[int]) -> None:
    """通知IDから削除の実行をする

    Args:
        notification_ids (tuple[int]): 通知IDのリスト
    """
    col_size = ",".join(["%s"] * len(notification_ids))
    database.table_update_sql(
        sql=f"""
        delete from genshin_notification
        where notification_id in ({col_size})
        """,
        data=notification_ids,
    )


def add_notification(type_id: int, bot_id: int, user_id: int, guild_id: int, notification_time: datetime, plan_time: datetime) -> None:
    """ユーザーが新規で通知を登録する為のデータ

    Args:
        type_id (int): 通知のタイプのID
        bot_id (int): BOT ID
        user_id (int): ユーザーID
        guild_id (int): ギルドID
        notification_time (datetime): 通知を行う時刻
    """
    database.table_update_sql(
        sql="""
        insert into genshin_notification
        (type_id, bot_id, user_id, guild_id, notification_time, plan_time)
        values
        (%s, %s, %s, %s, %s, %s)
        """,
        data=(
            type_id,
            bot_id,
            user_id,
            guild_id,
            notification_time,
            plan_time,
        )
    )


def get_notification_channel(guild_id: int) -> int:
    """通知チャンネルがそのギルドで登録されているかをチェックします
    Args:
        guild_id (int): GUILD ID

    Raises:
        ValueError: データベースに登録されていない場合エラーをraiseします

    Returns:
        int: channel_idを返します
    """
    result = database.load_data_sql(
        sql="""
        select channel_id from notification_channel where guild_id = %s
        """,
        data=(guild_id,),
    )
    if len(result) == 0:
        raise ValueError("channel not found")
    return result[0][0]


def set_notification_channel(guild_id: int, channel_id: int) -> None:
    database.table_update_sql(
        sql="""
        INSERT INTO notification_channel (guild_id, channel_id)
        VALUES (%s, %s)
        ON CONFLICT (guild_id)
        DO UPDATE SET channel_id = %s
        """,
        data=(guild_id, channel_id, channel_id,),
    )
