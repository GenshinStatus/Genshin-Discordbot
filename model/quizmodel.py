from lib.sql import database
from typing import Tuple
from datetime import datetime


class QuizData:
    """クイズ構造体クラス
    """

    def __init__(
        self,
        quiz_id: int,
        user_id: int,
        quiz_data: str,
        ansewr: str,
        options: list[str],
        image_url: str,
        created_at: datetime,
        global_auth_flg: bool,
        global_auth_user_id: int,
    ):
        self.quiz_id = quiz_id
        self.user_id = user_id
        self.quiz_data = quiz_data
        self.ansewr = ansewr
        self.options = options
        self.image_url = image_url
        self.created_at = created_at
        self.global_auth_flg = global_auth_flg
        self.global_auth_user_id = global_auth_user_id


def guild_quiz_list(guild_id: int, auth_flg: bool) -> list[QuizData]:
    result: Tuple = database.load_data_sql(
        sql="""
            select 
                quiz_id,
                user_id,
                quiz_data,
                answer,
                options,
                image_url,
                created_at,
                global_auth_flg,
                global_auth_user_id
            from
                genshin_quiz
            inner join
                guilds_own_quiz using(quiz_id)
            where
                auth_flg =%s
            """,
        data=(guild_id, auth_flg,),
    )
    return [QuizData(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10]) for v in result]


def global_quiz_list(global_auth_flg: bool) -> list[QuizData]:
    result: Tuple = database.load_data_sql(
        sql="""
            select 
                quiz_id,
                user_id,
                quiz_data,
                answer,
                options,
                image_url,
                created_at,
                global_auth_flg,
                global_auth_user_id
            from
                genshin_quiz
            where
                global_auth_flg =%s
            """,
        data=(global_auth_flg,),
    )
    return [QuizData(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10]) for v in result]


def all_quiz_search(guild_id: int, auth_flg: bool) -> list[QuizData]:
    result: Tuple = database.load_data_sql(
        sql="""
            select 
                quiz_id,
                user_id,
                quiz_data,
                answer,
                options,
                image_url,
                created_at,
                global_auth_flg,
                global_auth_user_id 
            from 
                genshin_quiz
            left join
                guild_own_quiz using(quiz_id)
            where
                global_auth_flg = true
                or guild_id =%s
                and auth_flg =%s
            """,
        data=(guild_id, auth_flg,),
    )
    return [QuizData(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10]) for v in result]


def add_quiz(
    guild_id: int,
    user_id: int,
    quiz_data: str,
    answer: str,
    options: list[str],
    image: str,
):
    database.table_update_sql(
        sql="""
        insert into genshin_quiz
        (
            guild_id,
            user_id,
            quiz_data,
            answer,
            options,
            image_udl
        )
        values
            (%s, %s, %s, %s, %s, %s)
        """,
        data=(
            guild_id,
            user_id,
            quiz_data,
            answer,
            options,
            image
        )
    )


def guild_apporaval_application(guild_id: int, user_id: int):
    database.table_update_sql(
        sql="""
        insert into guilds_own_quiz
        (
            quiz_id,
            guild_id
        )
        values(%s, %s)
        """
    )


def delete_quiz(quiz_id: int,):
    database.table_update_sql(
        sql="""
        delete from genshin_quiz
        where quiz_id = %s
        """,
        data=(quiz_id,),
    )
    database.table_update_sql(
        sql="""
        delete from guilds_own_quiz
        where quiz_id = %s
        """,
        data=(quiz_id,),
    )


def update_quiz(
    quiz_id: int,
    quiz_data: str,
    answer: str,
    options: list[str],
    image_url: str,
):
    database.table_update_sql(
        sql="""
        update
            genshin_quiz
        set
            quiz_data = %s,
            answer = %s,
            options = %s,
            image_url = %s
            global_auth_flg = false,
            global_auth_user_id = null
        where
            quiz_id = %s 
        """,
        data=(quiz_data, answer, options, image_url, quiz_id,),
    )
    database.table_update_sql(
        sql="""
        update
            guilds_own_quiz
        set
            auth_flg = false,
            auth_user_id = null
        where
            quiz_id = %s 
        """,
        data=(quiz_id,),
    )


def get_quiz_channel(guild_id: int) -> int:
    result: Tuple = database.load_data_sql(
        sql="""
            select 
                channel_id 
            from 
                quiz_channels
            where
                guild_id = %s 
            """,
        data=(guild_id,),
    )

    return result[0][0]


def set_quiz_channel(guild_id: int, channel_id: int):
    database.table_update_sql(
        sql="""
        insert into quiz_channels(guid, channel_id)
        values(%s, %s)
        on conflict (guild_id)
        do update set channel_id =%s
        """,
        data=(guild_id, channel_id, channel_id,),
    )


def remove_quiz_channel(guild_id: int):
    database.table_update_sql(
        sql="""
        delete from quiz_channels
        where guild_id = %s
        """,
        data=(guild_id,),
    )
